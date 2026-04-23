#!/usr/bin/env python3
"""
Project Root Detector for LSP Extraction

Detects sub-project boundaries in monorepos using static marker-file analysis
and recommends optimal scan roots for each language. Designed to be run before
1_extract_w_lsp.py to avoid 70%+ function loss from LSP servers failing to
index sub-projects properly.

Usage:
    python 0_detect_project_roots.py -d <directory> [-l <language>] [--docker] [--semgrep] [--json]
"""

import argparse
import fnmatch
import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import uuid
import xml.etree.ElementTree as ET
from collections import defaultdict, deque


# ──────────────────────────────────────────────────────────────────────────────
# C# project setup functions (merged from fix_csproj_for_lsp.py
# and partition_csharp.py)
# ──────────────────────────────────────────────────────────────────────────────


def find_all_projects(decompiled_dir):
    """Find all .csproj files and map AssemblyName -> (dir_name, csproj_relative_path)."""
    projects = {}  # AssemblyName -> list of (dir_name, csproj_filename)

    # Check subdirectories (multi-assembly layout: decompiled/ASSEMBLY_A/A.csproj)
    for d in sorted(os.listdir(decompiled_dir)):
        dp = os.path.join(decompiled_dir, d)
        if not os.path.isdir(dp):
            continue
        for f in os.listdir(dp):
            if f.endswith('.csproj'):
                _register_csproj(os.path.join(dp, f), d, f, projects)

    # Also check root directory (single-project layout: project/Project.csproj)
    for f in sorted(os.listdir(decompiled_dir)):
        if f.endswith('.csproj'):
            _register_csproj(os.path.join(decompiled_dir, f), ".", f, projects)

    return projects


def _register_csproj(csproj_path, dir_name, filename, projects):
    """Parse a .csproj and register it in the projects map."""
    try:
        tree = ET.parse(csproj_path)
        root = tree.getroot()
        asm_el = root.find('.//AssemblyName')
        if asm_el is not None and asm_el.text:
            asm_name = asm_el.text
        else:
            # Sdk-style projects use filename as assembly name
            asm_name = os.path.splitext(filename)[0]
        projects.setdefault(asm_name, []).append((dir_name, filename))
    except Exception as e:
        print(f"  WARN: Could not parse {csproj_path}: {e}")


_dll_cache = {}  # assembly_name -> path or None

def _find_dll(assembly_name, decompiled_dir):
    """Search for a DLL matching assembly_name in known locations."""
    if assembly_name in _dll_cache:
        return _dll_cache[assembly_name]

    # Look for a DLLs directory next to the decompiled dir (e.g., ../dlls_patched/)
    parent = os.path.dirname(os.path.abspath(decompiled_dir))
    search_dirs = []
    for d in os.listdir(parent):
        dp = os.path.join(parent, d)
        if os.path.isdir(dp) and 'dll' in d.lower():
            search_dirs.append(dp)

    # Also check a "lib" directory at the decompiled level
    lib_dir = os.path.join(decompiled_dir, '_lib')
    if os.path.isdir(lib_dir):
        search_dirs.append(lib_dir)

    for search_dir in search_dirs:
        # Case-insensitive search
        for f in os.listdir(search_dir):
            fname_lower = f.lower()
            target = assembly_name.lower() + '.dll'
            if fname_lower == target:
                result = os.path.join(search_dir, f)
                _dll_cache[assembly_name] = result
                return result

    _dll_cache[assembly_name] = None
    return None


def fix_csproj(csproj_path, assembly_map, decompiled_dir):
    """Fix a single .csproj file."""
    tree = ET.parse(csproj_path)
    root = tree.getroot()

    project_dir = os.path.dirname(csproj_path)
    project_dirname = os.path.basename(project_dir)

    # 1. TargetFramework — leave as-is for OmniSharp compatibility
    # OmniSharp handles net45/net48 with FrameworkPathOverride env var

    # 2. Collect all Reference elements
    references_to_remove = []
    project_references_to_add = []

    for item_group in root.findall('.//ItemGroup'):
        for ref in item_group.findall('Reference'):
            include = ref.get('Include', '')
            if not include:
                continue

            # Check if this reference maps to a sibling project
            if include in assembly_map:
                entries = assembly_map[include]
                # Pick the first one that isn't ourselves
                target = None
                for dir_name, csproj_name in entries:
                    if dir_name != project_dirname:
                        target = (dir_name, csproj_name)
                        break

                if target:
                    rel_path = os.path.join('..', target[0], target[1])
                    references_to_remove.append((item_group, ref))
                    project_references_to_add.append(rel_path)
                    continue

            # For non-System references without a sibling project, try to find
            # the DLL in a known directory and add a HintPath
            if not include.startswith('System') and include != 'mscorlib' and include != 'Microsoft.CSharp':
                dll_path = _find_dll(include, decompiled_dir)
                if dll_path:
                    # Add or update HintPath element
                    hp = ref.find('HintPath')
                    if hp is None:
                        hp = ET.SubElement(ref, 'HintPath')
                    hp.text = dll_path

    # Remove old references
    for item_group, ref in references_to_remove:
        item_group.remove(ref)

    # Add ProjectReferences
    if project_references_to_add:
        # Find or create ItemGroup for ProjectReferences
        proj_ig = ET.SubElement(root, 'ItemGroup')
        for rel_path in sorted(set(project_references_to_add)):
            pr = ET.SubElement(proj_ig, 'ProjectReference')
            pr.set('Include', rel_path)

    # Write back
    ET.indent(tree, space='  ')
    tree.write(csproj_path, xml_declaration=None, encoding='unicode')


def create_solution(decompiled_dir, projects):
    """Create a .sln file that includes all projects.

    The .sln is placed at decompiled_dir level so OmniSharp can find
    all sibling projects via relative paths.
    """
    # Remove any stale .sln files in project subdirectories
    for d in os.listdir(decompiled_dir):
        dp = os.path.join(decompiled_dir, d)
        if os.path.isdir(dp):
            for f in os.listdir(dp):
                if f.endswith('.sln'):
                    stale = os.path.join(dp, f)
                    os.remove(stale)
                    print(f"  Removed stale {stale}")

    # Deduplicate: when multiple projects share the same AssemblyName (e.g., GAC variants),
    # OmniSharp/Roslyn silently breaks. Keep only one per AssemblyName — prefer the one
    # with more .cs files (the "real" one, not the deployment wrapper).
    for asm_name, entries in list(projects.items()):
        if len(entries) > 1:
            # Pick the entry with the most source files
            scored = []
            for dir_name, csproj_name in entries:
                proj_dir = os.path.join(decompiled_dir, dir_name) if dir_name != "." else decompiled_dir
                cs_count = sum(1 for r, _, fs in os.walk(proj_dir) for f in fs if f.endswith('.cs'))
                scored.append((cs_count, dir_name, csproj_name))
            scored.sort(reverse=True)
            kept = scored[0]
            skipped = scored[1:]
            print(f"  \u26a0 Duplicate AssemblyName '{asm_name}': keeping {kept[1]} ({kept[0]} files), "
                  f"excluding {', '.join(d for _, d, _ in skipped)}")
            projects[asm_name] = [(kept[1], kept[2])]

    # Name the .sln after the parent directory (e.g., "decompiled" -> "decompiled.sln")
    dir_name = os.path.basename(os.path.normpath(decompiled_dir))
    sln_name = f"{dir_name}.sln" if dir_name else "Project.sln"
    sln_path = os.path.join(decompiled_dir, sln_name)

    lines = [
        '',
        'Microsoft Visual Studio Solution File, Format Version 12.00',
        '# Visual Studio Version 17',
        'VisualStudioVersion = 17.0.0.0',
        'MinimumVisualStudioVersion = 10.0.0.0',
    ]

    project_guids = []
    for asm_name, entries in sorted(projects.items()):
        for dir_name, csproj_name in entries:
            # Deterministic GUID from project path
            guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{dir_name}/{csproj_name}")).upper()
            # Use forward slashes — OmniSharp on Linux handles both
            rel_path = f"{dir_name}/{csproj_name}"
            lines.append(f'Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{dir_name}", "{rel_path}", "{{{guid}}}"')
            lines.append('EndProject')
            project_guids.append(guid)

    lines.append('Global')
    lines.append('\tGlobalSection(SolutionConfigurationPlatforms) = preSolution')
    lines.append('\t\tDebug|Any CPU = Debug|Any CPU')
    lines.append('\tEndGlobalSection')
    lines.append('\tGlobalSection(ProjectConfigurationPlatforms) = postSolution')
    for guid in project_guids:
        lines.append(f'\t\t{{{guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU')
        lines.append(f'\t\t{{{guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU')
    lines.append('\tEndGlobalSection')
    lines.append('EndGlobal')
    lines.append('')

    with open(sln_path, 'w') as f:
        f.write('\n'.join(lines))
    print(f"  Created {sln_path}")


def create_directory_build_props(decompiled_dir):
    """Create Directory.Build.props for .NET Framework reference assembly resolution.

    On Linux (e.g., inside Docker), MSBuild needs to know where the net48
    reference assemblies are. The sa-tool Docker image installs them at
    /tmp/netfx-refs/net48pkg/build/. This file tells MSBuild to use that
    path, and also works if FrameworkPathOverride env var is set.
    """
    props_path = os.path.join(decompiled_dir, 'Directory.Build.props')
    if os.path.exists(props_path):
        print(f"  Directory.Build.props already exists, skipping")
        return

    # Detect common net48 reference assembly locations
    candidates = [
        '/tmp/netfx-refs/net48pkg/build/',           # sa-tool Docker image
        os.path.expanduser('~/.nuget/packages/microsoft.netframework.referenceassemblies.net48/1.0.3/build/'),
    ]
    ref_path = None
    for c in candidates:
        if os.path.isdir(c):
            ref_path = c
            break

    if not ref_path:
        # Check FrameworkPathOverride env var
        fpo = os.environ.get('FrameworkPathOverride', '')
        if fpo and os.path.isdir(fpo):
            # FrameworkPathOverride is set, MSBuild will use it — no props needed
            print(f"  FrameworkPathOverride set to {fpo}, skipping Directory.Build.props")
            return
        print(f"  WARNING: Could not find net48 reference assemblies, skipping Directory.Build.props")
        print(f"  OmniSharp may fail to resolve System.* types. Set FrameworkPathOverride or install")
        print(f"  Microsoft.NETFramework.ReferenceAssemblies.net48 NuGet package.")
        return

    content = f"""<Project>
  <PropertyGroup>
    <TargetFrameworkRootPath>{ref_path}</TargetFrameworkRootPath>
    <EnableFrameworkPathOverride>false</EnableFrameworkPathOverride>
    <NoStdLib>true</NoStdLib>
  </PropertyGroup>
  <ItemGroup Condition="'$(TargetFrameworkIdentifier)' == '.NETFramework'">
    <Reference Include="mscorlib" Pack="false" />
  </ItemGroup>
</Project>
"""
    with open(props_path, 'w') as f:
        f.write(content)
    print(f"  Created Directory.Build.props (ref assemblies: {ref_path})")


def _break_circular_deps(sln_root):
    """Detect and break circular ProjectReference chains in csproj files.

    OmniSharp's ProjectManager.ProcessQueue throws ArgumentException on circular
    project references, causing an infinite retry loop that blocks all LSP requests.

    For each circular pair A <-> B, we keep the direction that preserves the most
    security-relevant call edges:
    1. Keep refs FROM larger projects (more code = more call sites to track)
    2. Keep refs TO security-sensitive modules (identity, auth, crypto, serialization)
    3. Remove from the project that is the "dependency" (fewer dependents)
    """
    deps = {}
    csproj_files = {}
    file_counts = {}

    for dirname in sorted(os.listdir(sln_root)):
        csproj = os.path.join(sln_root, dirname, f"{dirname}.csproj")
        if not os.path.exists(csproj):
            continue
        csproj_files[dirname] = csproj
        deps[dirname] = set()
        file_counts[dirname] = sum(1 for r, _, fs in os.walk(os.path.join(sln_root, dirname))
                                   for f in fs if f.endswith('.cs'))
        try:
            content = open(csproj).read()
            for m in re.finditer(r'<ProjectReference\s+Include="([^"]+)"', content):
                ref_path = m.group(1).replace('\\', '/')
                ref_dir = ref_path.split('/')[-2] if '/' in ref_path else ref_path.replace('.csproj', '')
                if os.path.isdir(os.path.join(sln_root, ref_dir)):
                    deps[dirname].add(ref_dir)
        except:
            pass

    # Find circular pairs
    circular = []
    for a in deps:
        for b in deps.get(a, set()):
            if b in deps and a in deps[b] and (b, a) not in circular:
                circular.append((a, b))

    if not circular:
        print("    No circular dependencies found ✓")
        return

    # Count how many projects depend on each (reverse dep count = "how core is it")
    dependents = {p: 0 for p in deps}
    for p, p_deps in deps.items():
        for d in p_deps:
            if d in dependents:
                dependents[d] += 1

    print(f"    Found {len(circular)} circular dependency pair(s):")
    for a, b in circular:
        # Heuristic: keep the ref FROM the project with more files (more call sites)
        # and TO the project that fewer others depend on (leaf/feature module).
        # This preserves: core_platform → feature_module edges (security-relevant)
        # and removes: feature_module → core_platform edges (less interesting)
        a_score = file_counts.get(a, 0)
        b_score = file_counts.get(b, 0)

        if a_score >= b_score:
            # A has more code — keep A→B, remove B→A
            remove_from, remove_ref, keep_from, keep_ref = b, a, a, b
        else:
            # B has more code — keep B→A, remove A→B
            remove_from, remove_ref, keep_from, keep_ref = a, b, b, a

        csproj = csproj_files.get(remove_from)
        if not csproj:
            continue
        try:
            content = open(csproj).read()
            pattern = rf'<ProjectReference\s+Include="[^"]*{re.escape(remove_ref)}[^"]*\.csproj"\s*/>'
            new_content = re.sub(pattern, '', content)
            if new_content != content:
                open(csproj, 'w').write(new_content)
                print(f"    ✓ Broke {a} <-> {b}: keep {keep_from}→{keep_ref} "
                      f"({file_counts.get(keep_from,0)} files), "
                      f"removed {remove_from}→{remove_ref} "
                      f"({file_counts.get(remove_from,0)} files)")
            else:
                print(f"    ⚠ Could not find ref pattern in {remove_from} for {remove_ref}")
        except Exception as e:
            print(f"    ✗ Error breaking {a} <-> {b}: {e}")


def _run_fix_csproj_for_lsp(sln_root):
    """Run the fix_csproj_for_lsp pipeline directly (was previously a subprocess call)."""
    print(f"  Scanning {sln_root} for .csproj files...")
    projects = find_all_projects(sln_root)

    # Build flat assembly -> (dir, csproj) map
    assembly_map = {}
    for asm_name, entries in projects.items():
        assembly_map[asm_name] = entries

    total_projects = sum(len(v) for v in projects.values())
    print(f"  Found {total_projects} projects ({len(projects)} unique assembly names)")

    # Fix each csproj
    print("  Fixing .csproj files...")
    for asm_name, entries in sorted(projects.items()):
        for dir_name, csproj_name in entries:
            csproj_path = os.path.join(sln_root, dir_name, csproj_name)
            print(f"    Fixing {dir_name}/{csproj_name}")
            fix_csproj(csproj_path, assembly_map, sln_root)

    # Break circular ProjectReference chains.
    # OmniSharp's ProcessQueue throws ArgumentException on circular refs, which causes
    # WaitForQueueEmptyAsync to loop forever, blocking ALL codestructure/findusages requests.
    # Detect cycles and remove one direction of each circular pair.
    print("  Checking for circular ProjectReference chains...")
    _break_circular_deps(sln_root)

    # Create solution
    print("  Creating solution file...")
    create_solution(sln_root, projects)

    # Create Directory.Build.props
    create_directory_build_props(sln_root)


def parse_dependency_graph(decompiled_dir):
    """Parse all .csproj files and build the dependency graph.

    Returns:
        deps: dict[project_name -> set of dependency project names]
        csproj_paths: dict[project_name -> relative csproj path]
    """
    deps = defaultdict(set)
    csproj_paths = {}

    for dirname in sorted(os.listdir(decompiled_dir)):
        dirpath = os.path.join(decompiled_dir, dirname)
        if not os.path.isdir(dirpath) or dirname.startswith('.') or dirname.startswith('scan_group_'):
            continue

        csproj = os.path.join(dirpath, f"{dirname}.csproj")
        if not os.path.exists(csproj):
            # Try finding any .csproj in the directory
            for f in os.listdir(dirpath):
                if f.endswith('.csproj'):
                    csproj = os.path.join(dirpath, f)
                    break
            else:
                continue

        csproj_paths[dirname] = os.path.relpath(csproj, decompiled_dir)

        try:
            with open(csproj) as f:
                content = f.read()
        except:
            continue

        # Extract ProjectReference entries
        for match in re.finditer(r'<ProjectReference\s+Include="([^"]+)"', content):
            ref_path = match.group(1).replace('\\', '/')
            # Extract directory name: ../STSOM/STSOM.csproj -> STSOM
            ref_dir = ref_path.split('/')[-2] if '/' in ref_path else ref_path.replace('.csproj', '')
            if ref_dir in os.listdir(decompiled_dir):
                deps[dirname].add(ref_dir)

        # Ensure every project is in deps (even with no deps)
        if dirname not in deps:
            deps[dirname] = set()

    # Deduplicate projects with same AssemblyName (e.g., GAC variants).
    # OmniSharp/Roslyn silently breaks when two projects share an AssemblyName.
    asm_to_dirs = defaultdict(list)
    for dirname in list(deps.keys()):
        csproj = os.path.join(decompiled_dir, csproj_paths.get(dirname, ''))
        if os.path.exists(csproj):
            try:
                tree = ET.parse(csproj)
                for elem in tree.iter():
                    if elem.tag.endswith('AssemblyName') and elem.text:
                        asm_to_dirs[elem.text].append(dirname)
                        break
            except:
                pass

    for asm_name, dirs in asm_to_dirs.items():
        if len(dirs) > 1:
            # Keep the one with the most .cs files
            scored = []
            for d in dirs:
                cs_count = sum(1 for r, _, fs in os.walk(os.path.join(decompiled_dir, d))
                               for f in fs if f.endswith('.cs'))
                scored.append((cs_count, d))
            scored.sort(reverse=True)
            kept = scored[0]
            for _, d in scored[1:]:
                print(f"  \u26a0 Duplicate AssemblyName '{asm_name}': excluding {d} (keeping {kept[1]})")
                del deps[d]
                del csproj_paths[d]
                # Remove references to excluded project
                for p in deps:
                    deps[p].discard(d)

    return dict(deps), csproj_paths


def compute_transitive_deps(deps, project):
    """BFS to find all transitive dependencies of a project."""
    visited = set()
    queue = deque([project])
    while queue:
        p = queue.popleft()
        if p in visited:
            continue
        visited.add(p)
        for dep in deps.get(p, set()):
            if dep not in visited:
                queue.append(dep)
    visited.discard(project)  # Don't include self
    return visited


def count_files(decompiled_dir):
    """Count .cs files per project (excluding obj/ directories)."""
    counts = {}
    for dirname in sorted(os.listdir(decompiled_dir)):
        dirpath = os.path.join(decompiled_dir, dirname)
        if not os.path.isdir(dirpath) or dirname.startswith('.') or dirname.startswith('scan_group_'):
            continue
        count = 0
        for root, dirs, files in os.walk(dirpath):
            # Skip obj directories
            if '/obj/' in root + '/' or root.endswith('/obj'):
                continue
            count += sum(1 for f in files if f.endswith('.cs'))
        counts[dirname] = count
    return counts


def enumerate_project_subdirs(decompiled_dir, project_name):
    """List a project's subdirectories with their file counts."""
    proj_dir = os.path.join(decompiled_dir, project_name)
    if not os.path.isdir(proj_dir):
        return []

    subdirs = []
    root_files = 0

    for entry in sorted(os.listdir(proj_dir)):
        full = os.path.join(proj_dir, entry)
        if entry in ('obj', 'bin', 'Properties') or entry.endswith(('.csproj', '.sln', '.json')):
            continue
        if os.path.isdir(full):
            count = sum(1 for r, _, fs in os.walk(full)
                       for f in fs if f.endswith('.cs') and '/obj/' not in r + '/')
            if count > 0:
                subdirs.append((count, entry))
        elif entry.endswith('.cs'):
            root_files += 1

    if root_files > 0:
        subdirs.append((root_files, '__ROOT__'))

    subdirs.sort(reverse=True)
    return subdirs


def split_large_project(subdirs, n_chunks):
    """Split a project's subdirectories into n_chunks of roughly equal file count."""
    chunks = [[] for _ in range(n_chunks)]
    chunk_sizes = [0] * n_chunks

    for count, name in subdirs:
        idx = chunk_sizes.index(min(chunk_sizes))
        chunks[idx].append((count, name))
        chunk_sizes[idx] += count

    return chunks, chunk_sizes


def auto_detect_groups(deps, file_counts, chunk_size=2000):
    """Determine number of chunks from total file count and chunk_size.

    This is a thin compatibility shim — the real work now happens in
    partition_projects_by_chunk_size().  Kept so that run_pipeline()
    and other callers that only need "how many groups" can still call
    a single function.
    """
    total_files = sum(file_counts.values())
    if total_files <= chunk_size:
        return 1
    return max(2, -(-total_files // chunk_size))  # ceil division


def detect_large_projects(file_counts, chunk_size=2000):
    """Detect projects that should be split based on chunk_size threshold.

    A project is "large" if it has more files than chunk_size.  It gets
    split into ceil(count / chunk_size) sub-chunks by subdirectory.
    """
    large = {}
    for proj, count in file_counts.items():
        if count > chunk_size:
            n_chunks = max(2, -(-count // chunk_size))  # ceil division
            large[proj] = n_chunks

    return large


def partition_projects(deps, file_counts, split_projects, n_groups=None, chunk_size=2000):
    """Bin-pack projects into chunks of ~chunk_size files each.

    Large projects are pre-split into subdirectory chunks.  Small projects
    are batched together until the running total reaches ~chunk_size, then
    a new chunk is started.  The number of chunks emerges from the data.

    Args:
        split_projects: dict[project_name -> (chunks, chunk_sizes)]
            where chunks is list of [(file_count, subdir_name), ...] per chunk
        n_groups: ignored (kept for API compat); chunk count is derived from data
        chunk_size: target files per chunk (default 2000)

    Returns list of groups, each group is a dict with:
        scan_projects: list of project names to scan
        split_chunks: list of (project_name, chunk_index, subdir_list) tuples
        total_files: total files to scan
    """
    # Create scan units: regular projects + split project chunks
    units = []
    split_project_names = set(split_projects.keys())

    for proj, count in sorted(file_counts.items(), key=lambda x: -x[1]):
        if proj in split_project_names:
            continue  # Handled as chunks
        units.append({
            'projects': [proj],
            'files': count,
            'split_chunk': None,
        })

    for proj_name, (chunks, chunk_sizes) in split_projects.items():
        for i, (chunk, size) in enumerate(zip(chunks, chunk_sizes)):
            units.append({
                'projects': [],  # The project is added to sln via deps, not as scan target
                'files': size,
                'split_chunk': (proj_name, i, [name for _, name in chunk]),
            })

    # Sort by file count descending for greedy bin packing
    units.sort(key=lambda x: -x['files'])

    # Greedy bin-packing: place each unit into the lightest existing chunk,
    # or start a new chunk if the lightest one is already at/above chunk_size.
    groups = []

    for unit in units:
        placed = False
        if groups:
            # Find the lightest chunk
            min_idx = min(range(len(groups)), key=lambda i: groups[i]['total_files'])
            if groups[min_idx]['total_files'] + unit['files'] <= chunk_size * 1.25:
                # Allow 25% overshoot to avoid many tiny tail chunks
                groups[min_idx]['scan_projects'].extend(unit['projects'])
                groups[min_idx]['total_files'] += unit['files']
                if unit['split_chunk'] is not None:
                    groups[min_idx]['split_chunks'].append(unit['split_chunk'])
                placed = True

        if not placed:
            new_group = {
                'scan_projects': list(unit['projects']),
                'split_chunks': [],
                'total_files': unit['files'],
            }
            if unit['split_chunk'] is not None:
                new_group['split_chunks'].append(unit['split_chunk'])
            groups.append(new_group)

    # If we ended up with no groups (empty input), return one empty group
    if not groups:
        groups = [{'scan_projects': [], 'split_chunks': [], 'total_files': 0}]

    return groups


def compute_sln_projects(group, deps, all_projects):
    """Compute the full set of projects needed in a group's .sln.

    Includes: group's scan projects + split chunk parents + all transitive deps.
    """
    sln_projects = set()

    # Add scan projects
    for proj in group['scan_projects']:
        sln_projects.add(proj)

    # Add parent projects for any split chunks
    for proj_name, chunk_idx, subdirs in group.get('split_chunks', []):
        sln_projects.add(proj_name)

    # Add transitive deps for all projects in the sln
    to_process = set(sln_projects)
    while to_process:
        proj = to_process.pop()
        for dep in deps.get(proj, set()):
            if dep not in sln_projects and dep in all_projects:
                sln_projects.add(dep)
                to_process.add(dep)

    return sln_projects


def build_include_regex(group):
    """Build --include-paths regex for a group."""
    parts = []

    # Regular projects
    for proj in group['scan_projects']:
        parts.append(re.escape(proj) + '/')

    # Split project subdirectories
    for proj_name, chunk_idx, subdirs in group.get('split_chunks', []):
        for subdir in subdirs:
            if subdir == '__ROOT__':
                parts.append(re.escape(proj_name) + '/[^/]+\\.cs$')
            else:
                parts.append(re.escape(proj_name) + '/' + re.escape(subdir) + '/')

    if not parts:
        return ''

    return ','.join(parts)


def write_sln(sln_path, projects, csproj_paths):
    """Write a .sln file for the given project set."""
    lines = [
        '',
        'Microsoft Visual Studio Solution File, Format Version 12.00',
        '# Visual Studio Version 17',
        'VisualStudioVersion = 17.0.0.0',
        'MinimumVisualStudioVersion = 10.0.0.0',
    ]

    guids = []
    for proj in sorted(projects):
        if proj not in csproj_paths:
            continue
        guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, csproj_paths[proj])).upper()
        rel_path = csproj_paths[proj]
        lines.append(f'Project("{{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}}") = "{proj}", "{rel_path}", "{{{guid}}}"')
        lines.append('EndProject')
        guids.append(guid)

    lines.append('Global')
    lines.append('\tGlobalSection(SolutionConfigurationPlatforms) = preSolution')
    lines.append('\t\tDebug|Any CPU = Debug|Any CPU')
    lines.append('\tEndGlobalSection')
    lines.append('\tGlobalSection(ProjectConfigurationPlatforms) = postSolution')
    for guid in guids:
        lines.append(f'\t\t{{{guid}}}.Debug|Any CPU.ActiveCfg = Debug|Any CPU')
        lines.append(f'\t\t{{{guid}}}.Debug|Any CPU.Build.0 = Debug|Any CPU')
    lines.append('\tEndGlobalSection')
    lines.append('EndGlobal')
    lines.append('')

    with open(sln_path, 'w') as f:
        f.write('\n'.join(lines))




# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

SKIP_DIRS = {
    ".git", "node_modules", "vendor", "__pycache__", ".vscode",
    "build", "dist", "target", ".gradle", ".tox", ".mypy_cache",
    ".pytest_cache", "_build", ".bundle", ".eggs", ".hg", ".svn",
}

CACHE_REL = os.path.join(".vscode", "ext-static-analysis", "cache")
CACHE_CHECK_FILES = ["function_calls.json", "functions_html.json"]

PROJECT_MARKERS = {
    "ruby":       {"primary": ["Gemfile", "*.gemspec"], "workspace": []},
    "typescript": {"primary": ["package.json", "deno.json", "deno.jsonc"], "workspace": ["pnpm-workspace.yaml", "lerna.json", "nx.json", "turbo.json", "rush.json"]},
    "python":     {"primary": ["pyproject.toml", "setup.py", "setup.cfg"], "workspace": []},
    "rust":       {"primary": ["Cargo.toml"], "workspace": []},
    "go":         {"primary": ["go.mod"], "workspace": ["go.work"]},
    "java":       {"primary": ["pom.xml", "build.gradle", "build.gradle.kts"], "workspace": ["settings.gradle", "settings.gradle.kts"]},
    "kotlin":     {"primary": ["build.gradle.kts"], "workspace": ["settings.gradle.kts"]},
    "c#":         {"primary": ["*.csproj", "*.fsproj"], "workspace": ["*.sln", "*.slnx"]},
    "php":        {"primary": ["composer.json"], "workspace": []},
    "scala":      {"primary": ["build.sbt", "build.sc"], "workspace": []},
    "elixir":     {"primary": ["mix.exs"], "workspace": []},
    "haskell":    {"primary": ["*.cabal", "package.yaml"], "workspace": ["cabal.project", "stack.yaml"]},
    "ocaml":      {"primary": ["dune-project"], "workspace": ["dune-workspace"]},
    "zig":        {"primary": ["build.zig"], "workspace": []},
    "c":          {"primary": ["CMakeLists.txt", "compile_commands.json", "Makefile", "meson.build"], "workspace": []},
    "solidity":   {"primary": ["hardhat.config.js", "hardhat.config.ts", "foundry.toml", "truffle-config.js"], "workspace": []},
    "dart":       {"primary": ["pubspec.yaml"], "workspace": []},
    "swift":      {"primary": ["Package.swift"], "workspace": ["*.xcworkspace"]},
    "clojure":    {"primary": ["deps.edn", "project.clj", "shadow-cljs.edn"], "workspace": []},
    "erlang":     {"primary": ["rebar.config", "erlang.mk"], "workspace": []},
}

# Extensions used for file counting. Only actual source files — no stubs,
# declarations, build scripts, or generated artifacts.
LANGUAGE_EXTENSIONS = {
    "ruby": [".rb"],
    "typescript": [".js", ".jsx", ".ts", ".tsx", ".mjs", ".mts"],
    "python": [".py"],
    "rust": [".rs"],
    "go": [".go"],
    "java": [".java"],
    "kotlin": [".kt"],
    "c#": [".cs"],
    "php": [".php"],
    "scala": [".scala", ".sc"],
    "elixir": [".ex", ".exs"],
    "haskell": [".hs", ".lhs"],
    "ocaml": [".ml", ".mli"],
    "zig": [".zig"],
    "c": [".c", ".cc", ".cpp", ".cxx", ".m", ".mm", ".h", ".hh", ".hpp"],
    "solidity": [".sol"],
    "dart": [".dart"],
    "swift": [".swift"],
    "clojure": [".clj", ".cljs", ".cljc", ".edn"],
    "erlang": [".erl", ".hrl"],
    "bash": [".sh"],
    "lua": [".lua"],
    "groovy": [".groovy"],
    "powershell": [".ps1"],
    "asm": [".asm"],
}

# Whether the LSP server can handle monorepos from a single root
LSP_HANDLES_MONOREPO = {
    # "native" = LSP handles workspace natively, scan from workspace root
    "go": "native",
    "rust": "native",
    "java": "native",
    "kotlin": "native",
    "scala": "native",
    "python": "native",
    "dart": "native",

    # "solution" = OmniSharp scans from .sln root with --include-paths per project
    "c#": "solution",
    "typescript": "partial",
    "solidity": "partial",
    "elixir": "partial",
    "swift": "partial",

    # "none" = LSP needs per-project root — always recommend per-project scanning
    "ruby": "none",
    "php": "none",
    "c": "none",
    "zig": "none",
    "ocaml": "none",
    "haskell": "none",
    "clojure": "none",
    "erlang": "none",
    "bash": "none",
    "lua": "none",
    "groovy": "none",
    "powershell": "none",
    "asm": "none",
}

LSP_MONOREPO_NOTES = {
    "go":         "gopls handles go.work workspaces natively.",
    "rust":       "rust-analyzer handles Cargo workspaces natively.",
    "java":       "JDT LS handles Maven modules / Gradle multi-project natively.",
    "kotlin":     "Kotlin LS shares Gradle infrastructure with Java.",
    "scala":      "Metals supports multi-root sbt projects.",
    "python":     "Pyright handles multi-root reasonably.",
    "dart":       "Dart analysis server handles pub workspaces.",
    "c#":         "OmniSharp scans from .sln root. Each project runs as a parallel instance with --include-paths for cross-assembly resolution.",
    "typescript": "tsconfig resolution has known issues in monorepos.",
    "solidity":   "Nomic LS scans for configs but is not always reliable.",
    "elixir":     "ElixirLS handles umbrella projects, but not arbitrary multi-root.",
    "swift":      "sourcekit-lsp handles SPM packages; Xcode workspaces need per-project.",
    "ruby":       "Solargraph does not handle monorepo workspaces.",
    "php":        "Intelephense has performance issues with multi-root.",
    "c":          "clangd needs per-project compile_commands.json.",
    "zig":        "ZLS is single-project only.",
    "ocaml":      "ocamllsp relies on dune, not LSP workspace folders.",
    "haskell":    "HLS spawns per-folder server instances.",
    "clojure":    "clojure-lsp uses deps.edn/project.clj per project.",
    "erlang":     "erlang_ls works per rebar3 project.",
    "bash":       "No project concept in bash-language-server.",
    "lua":        "No project concept in lua-language-server.",
    "groovy":     "Limited LSP support.",
    "powershell": "Limited LSP support.",
    "asm":        "Limited LSP support.",
}

# Dependency install commands per language.
# Key: language name. Value: list of (lockfile_or_marker, install_command) tuples.
# The first matching lockfile/marker wins. Commands run inside the project root.
# All use --ignore-scripts or equivalent to avoid running arbitrary code.
# Language servers that auto-resolve deps (java, go, rust, scala, kotlin, dart)
# are intentionally omitted — their LSPs handle it internally.
INSTALL_COMMANDS = {
    "typescript": [
        ("pnpm-lock.yaml",   "pnpm install --ignore-scripts --frozen-lockfile 2>/dev/null || true"),
        ("yarn.lock",        "yarn install --ignore-scripts --frozen-lockfile 2>/dev/null || true"),
        ("package-lock.json","npm ci --ignore-scripts 2>/dev/null || true"),
        ("package.json",     "npm install --ignore-scripts 2>/dev/null || true"),
    ],
    "ruby": [
        ("Gemfile.lock",     "bundle install --no-cache --jobs 4 2>/dev/null || true"),
        ("Gemfile",          "bundle install --no-cache --jobs 4 2>/dev/null || true"),
    ],
    "php": [
        ("composer.lock",    "composer install --no-scripts --no-interaction 2>/dev/null || true"),
        ("composer.json",    "composer install --no-scripts --no-interaction 2>/dev/null || true"),
    ],
    "python": [
        ("requirements.txt", "pip install -r requirements.txt --target .venv/lib 2>/dev/null || true"),
        ("pyproject.toml",   "pip install -e . --target .venv/lib 2>/dev/null || true"),
    ],
    # C# omitted: OmniSharp resolves ProjectReferences without dotnet restore.
    # Decompiled projects have circular deps that cause restore to fail.
    "c": [
        ("CMakeLists.txt",   "cmake -B build -DCMAKE_EXPORT_COMPILE_COMMANDS=ON 2>/dev/null && ln -sf build/compile_commands.json . || true"),
        ("Makefile",         "bear -- make -n 2>/dev/null || compiledb make -n 2>/dev/null || true"),
    ],
    "ocaml": [
        ("dune-project",     "opam install . --deps-only --yes 2>/dev/null; dune build 2>/dev/null || true"),
    ],
    "haskell": [
        ("cabal.project",    "cabal update 2>/dev/null; cabal build --only-dependencies 2>/dev/null || true"),
        ("*.cabal",          "cabal update 2>/dev/null; cabal build --only-dependencies 2>/dev/null || true"),
        ("stack.yaml",       "stack build --only-dependencies 2>/dev/null || true"),
    ],
    "elixir": [
        ("mix.lock",         "mix deps.get 2>/dev/null || true"),
        ("mix.exs",          "mix deps.get 2>/dev/null || true"),
    ],
    "clojure": [
        ("deps.edn",         "clojure -P 2>/dev/null || true"),
        ("project.clj",      "lein deps 2>/dev/null || true"),
    ],
    "erlang": [
        ("rebar.lock",       "rebar3 get-deps 2>/dev/null || true"),
        ("rebar.config",     "rebar3 get-deps 2>/dev/null || true"),
    ],
}


def get_install_command(language, project_dir):
    """
    Return the dep install command for a project root, or None if not needed.
    Checks which lockfile/marker exists and returns the matching command.
    """
    entries = INSTALL_COMMANDS.get(language, [])
    for marker, cmd in entries:
        if "*" in marker:
            # Glob pattern — check if any file matches
            if any(fnmatch.fnmatch(f, marker) for f in os.listdir(project_dir)
                   if os.path.isfile(os.path.join(project_dir, f))):
                return cmd
        else:
            if os.path.exists(os.path.join(project_dir, marker)):
                return cmd
    return None


def _is_under_skipped(install_dir, skipped_dirs):
    """True if install_dir equals or lives under any path in skipped_dirs."""
    if not skipped_dirs:
        return False
    if install_dir in skipped_dirs:
        return True
    for s in skipped_dirs:
        if install_dir.startswith(s.rstrip(os.sep) + os.sep):
            return True
    return False


def get_install_roots(recommendations):
    """
    Return deduplicated list of (dir, language, install_cmd) for dep installation.
    Installs at every detected project root (workspace roots AND sub-packages).
    True workspaces (pnpm/yarn/npm/Cargo) make sub-package installs redundant but
    harmless; monorepos without hoisting (lerna/nx/rush, or sub-packages with their
    own lockfiles) rely on the per-sub-root install to get node_modules in place.
    """
    install_roots = []
    seen = set()
    for rec in recommendations:
        lang = rec["language"]
        dirs_to_install = [r["dir"] for r in rec["roots"]]

        for d in dirs_to_install:
            key = (d, lang)
            if key in seen:
                continue
            install_cmd = get_install_command(lang, d)
            if install_cmd:
                seen.add(key)
                install_roots.append((d, lang, install_cmd))

    return install_roots


# ──────────────────────────────────────────────────────────────────────────────
# Step 1: Walk directory tree and find all project markers
# ──────────────────────────────────────────────────────────────────────────────

def _matches_any_pattern(filename, patterns):
    """Check if filename matches any of the glob patterns."""
    for pat in patterns:
        if fnmatch.fnmatch(filename, pat):
            return pat
    return None


def _check_workspace_content(filepath, marker_filename):
    """
    Inspect file content to determine if it declares a workspace/monorepo.
    Returns True if workspace indicators are found.
    """
    try:
        with open(filepath, "r", errors="replace") as f:
            content = f.read()
    except (OSError, IOError):
        return False

    name_lower = marker_filename.lower()

    # Cargo.toml: [workspace] section
    if name_lower == "cargo.toml":
        return bool(re.search(r'^\s*\[workspace\]', content, re.MULTILINE))

    # package.json: "workspaces" key
    if name_lower == "package.json":
        return '"workspaces"' in content

    # go.work: presence alone = workspace root
    if name_lower == "go.work":
        return True

    # pom.xml: <modules> element
    if name_lower == "pom.xml":
        return "<modules>" in content

    # settings.gradle / settings.gradle.kts: include or includeBuild
    if name_lower in ("settings.gradle", "settings.gradle.kts"):
        return bool(re.search(r'\b(include|includeBuild)\b', content))

    # build.sbt: .aggregate(
    if name_lower == "build.sbt":
        return ".aggregate(" in content

    # mix.exs: apps_path
    if name_lower == "mix.exs":
        return "apps_path" in content

    # pubspec.yaml: workspace: key
    if name_lower == "pubspec.yaml":
        return bool(re.search(r'^\s*workspace\s*:', content, re.MULTILINE))

    # pyproject.toml: [tool.uv.workspace]
    if name_lower == "pyproject.toml":
        return bool(re.search(r'^\s*\[tool\.uv\.workspace\]', content, re.MULTILINE))

    # cabal.project: packages:
    if name_lower == "cabal.project":
        return bool(re.search(r'^\s*packages\s*:', content, re.MULTILINE))

    # stack.yaml: packages:
    if name_lower == "stack.yaml":
        return bool(re.search(r'^\s*packages\s*:', content, re.MULTILINE))

    # rush.json: "projects" array
    if name_lower == "rush.json":
        return '"projects"' in content

    # Workspace-only markers: presence alone indicates workspace
    presence_markers = {
        "pnpm-workspace.yaml", "lerna.json", "nx.json", "turbo.json",
        "dune-workspace",
    }
    if name_lower in presence_markers:
        return True

    # *.sln / *.slnx: presence indicates a solution workspace
    if name_lower.endswith(".sln") or name_lower.endswith(".slnx"):
        return True

    # *.xcworkspace: presence indicates Xcode workspace
    if name_lower.endswith(".xcworkspace"):
        return True

    # deno.json / deno.jsonc: "workspace" key
    if name_lower in ("deno.json", "deno.jsonc"):
        return '"workspace"' in content

    return False


def find_project_markers(root_dir, languages=None):
    """
    Walk directory tree and find all project marker files.

    Returns list of dicts:
        {dir, language, marker, is_workspace}
    """
    results = []
    languages_to_check = languages or list(PROJECT_MARKERS.keys())

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip ignored directories (modify dirnames in-place to prune walk)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('scan_group_')]

        for lang in languages_to_check:
            if lang not in PROJECT_MARKERS:
                continue
            markers = PROJECT_MARKERS[lang]

            # Check primary markers
            for fn in filenames:
                matched = _matches_any_pattern(fn, markers["primary"])
                if matched:
                    filepath = os.path.join(dirpath, fn)
                    # A primary marker might also declare a workspace via content
                    is_ws = _check_workspace_content(filepath, fn)
                    results.append({
                        "dir": dirpath,
                        "language": lang,
                        "marker": fn,
                        "is_workspace": is_ws,
                    })

            # Check workspace markers
            for fn in filenames:
                matched = _matches_any_pattern(fn, markers["workspace"])
                if matched:
                    filepath = os.path.join(dirpath, fn)
                    is_ws = _check_workspace_content(filepath, fn)
                    results.append({
                        "dir": dirpath,
                        "language": lang,
                        "marker": fn,
                        "is_workspace": is_ws,
                    })

    return results


# ──────────────────────────────────────────────────────────────────────────────
# Step 2: Count source files per detected root
# ──────────────────────────────────────────────────────────────────────────────

def count_source_files(directory, language):
    """Count files matching the language's extensions under directory."""
    exts = LANGUAGE_EXTENSIONS.get(language, [])
    if not exts:
        return 0

    ext_set = set(exts)
    count = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('scan_group_')]
        for fn in filenames:
            _, ext = os.path.splitext(fn)
            if ext in ext_set:
                count += 1
    return count


# ──────────────────────────────────────────────────────────────────────────────
# Step 3: Determine recommendations and hierarchy
# ──────────────────────────────────────────────────────────────────────────────

def deduplicate_roots(markers):
    """
    Deduplicate markers: keep one entry per (dir, language), preferring
    workspace markers over primary ones.
    """
    best = {}  # (dir, language) -> marker dict
    for m in markers:
        key = (m["dir"], m["language"])
        if key not in best or m["is_workspace"]:
            best[key] = m
    return list(best.values())


def compute_hierarchy(roots, root_dir):
    """
    For each root, find its parent root (if any) within the same language.
    A root B is a child of root A if A's directory is a proper ancestor of B's.

    Returns the roots list with 'parent' and 'children' fields added.
    """
    # Group by language
    by_lang = {}
    for r in roots:
        by_lang.setdefault(r["language"], []).append(r)

    for lang, lang_roots in by_lang.items():
        # Sort by path depth (shallowest first)
        lang_roots.sort(key=lambda r: r["dir"].count(os.sep))

        for r in lang_roots:
            r["parent"] = None
            r["children"] = []

        # For each root, find its nearest ancestor in the same language
        for i, child in enumerate(lang_roots):
            child_dir = child["dir"] + os.sep
            for j in range(i - 1, -1, -1):
                parent_dir = lang_roots[j]["dir"] + os.sep
                if child_dir.startswith(parent_dir):
                    child["parent"] = lang_roots[j]["dir"]
                    lang_roots[j]["children"].append(child["dir"])
                    break

    return roots


def build_recommendations(root_dir, markers):
    """
    Given deduplicated markers with file counts, produce recommendations
    per language.

    Returns list of recommendation dicts:
        {language, roots: [{dir, marker, files, is_workspace, parent, children}], strategy, note}
    """
    # Group by language
    by_lang = {}
    for m in markers:
        by_lang.setdefault(m["language"], []).append(m)

    recommendations = []

    for lang, roots in sorted(by_lang.items()):
        # Sort: workspace roots first, then by file count descending
        roots.sort(key=lambda r: (-int(r["is_workspace"]), -r["files"]))

        lsp_support = LSP_HANDLES_MONOREPO.get(lang, "none")
        has_workspace_root = any(r["is_workspace"] for r in roots)
        multi_root = len(roots) > 1

        if not multi_root:
            strategy = "single"
            note = f"Single project root detected."
        elif lsp_support == "solution":
            strategy = "solution"
            note = (
                f"{LSP_MONOREPO_NOTES.get(lang, '')} "
                f"Each project scanned in parallel from solution root with --include-paths."
            )
        elif lsp_support == "native" and has_workspace_root:
            strategy = "workspace"
            note = (
                f"{LSP_MONOREPO_NOTES.get(lang, '')} "
                f"Recommendation: scan from workspace root."
            )
        elif lsp_support == "native" and not has_workspace_root:
            strategy = "per-project"
            note = (
                f"{LSP_MONOREPO_NOTES.get(lang, '')} "
                f"No workspace file found — scanning per-project."
            )
        elif lsp_support == "partial":
            strategy = "per-project"
            note = (
                f"{LSP_MONOREPO_NOTES.get(lang, '')} "
                f"Recommendation: scan each sub-project individually (root-level might work)."
            )
        else:  # "none"
            strategy = "per-project"
            note = (
                f"{LSP_MONOREPO_NOTES.get(lang, '')} "
                f"Scanning from root would miss functions in sub-projects. "
                f"Recommendation: scan each sub-project individually."
            )

        recommendations.append({
            "language": lang,
            "roots": roots,
            "strategy": strategy,
            "note": note,
        })

    return recommendations


def get_scan_roots(rec):
    """
    Given a recommendation, return the list of directories to scan.
    For 'workspace' strategy, return only the workspace root(s).
    For 'solution' strategy (C#), return all project roots — each will
    scan from the solution root with --include-paths for parallelism.
    For 'per-project' or 'single', return all roots.
    """
    if rec["strategy"] == "workspace":
        ws_roots = [r for r in rec["roots"] if r["is_workspace"]]
        return ws_roots if ws_roots else rec["roots"]
    if rec["strategy"] == "solution":
        # Return non-workspace roots (individual csproj projects).
        # The workspace root (.sln) is used as -d, not as a scan target itself.
        non_ws = [r for r in rec["roots"] if not r["is_workspace"]]
        return non_ws if non_ws else rec["roots"]
    return rec["roots"]


def _find_solution_root(rec):
    """For C# 'solution' strategy, find the .sln workspace root directory.

    If no .sln exists (e.g., ILSpy decompilation only creates .csproj files),
    auto-creates one by running the C# project setup (fix csproj refs, create
    sln, Directory.Build.props).
    """
    ws_roots = [r for r in rec["roots"] if r["is_workspace"]]
    if ws_roots:
        return ws_roots[0]["dir"]

    # No .sln found — auto-create one from .csproj files
    # Find the common parent directory of all project roots
    all_dirs = [r["dir"] for r in rec["roots"]]
    if not all_dirs:
        return None

    # The solution root is the common parent of all project dirs
    sln_root = os.path.commonpath(all_dirs)
    if not os.path.isdir(sln_root):
        return None

    print(f"\n  Setting up C# project for OmniSharp (no .sln found)...")
    print(f"    ILSpy creates .csproj files but not .sln — creating automatically.")
    try:
        _run_fix_csproj_for_lsp(sln_root)
        # Verify .sln was created
        slns = [f for f in os.listdir(sln_root) if f.endswith('.sln')]
        if slns:
            print(f"    Created {slns[0]} with C# project setup complete.")
            return sln_root
        else:
            print(f"    WARNING: .sln creation failed — no .sln file found after setup")
            return None
    except Exception as e:
        print(f"    WARNING: C# project setup failed: {e}")
        return None


def get_dirs_at_depth(root_dir, depth, skip_dirs=None):
    """
    Return all directories at exactly `depth` levels below root_dir.
    depth=1 returns immediate subdirectories; depth=2 returns their children, etc.
    """
    skip = skip_dirs if skip_dirs is not None else SKIP_DIRS

    if depth <= 0:
        return [root_dir]

    result = []

    def _recurse(current, remaining):
        try:
            entries = sorted(os.listdir(current))
        except PermissionError:
            return
        for entry in entries:
            if entry in skip:
                continue
            path = os.path.join(current, entry)
            if os.path.isdir(path):
                if remaining == 1:
                    result.append(path)
                else:
                    _recurse(path, remaining - 1)

    _recurse(root_dir, depth)
    return sorted(result)


def copy_to_clipboard(text):
    """
    Copy text to system clipboard. Returns True on success.

    Strategy:
      1. Native tools (xclip/xsel/pbcopy) — work on host with X11/Wayland/macOS.
      2. OSC 52 terminal escape — works inside Docker/SSH when the terminal
         emulator supports it (VS Code, Windows Terminal, iTerm2, kitty, etc.).
    """
    for cmd in [["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"], ["pbcopy"]]:
        try:
            subprocess.run(cmd, input=text.encode(), check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue

    # OSC 52: works through Docker -it / SSH TTY if the terminal supports it
    try:
        import base64
        b64 = base64.b64encode(text.encode()).decode()
        sys.stdout.write(f"\033]52;c;{b64}\007")
        sys.stdout.flush()
        return True
    except Exception:
        return False


def check_scanned_dirs(dirs, semgrep_mode=False):
    """
    Check which directories already have non-empty scan cache data.

    Returns dict: {dir: {"function_calls.json": N, "functions_html.json": N}}
    (or {dir: {"semgrep.json": N}} in semgrep mode).
    Only includes directories with at least one non-zero count.
    """
    results = {}
    for d in dirs:
        counts = {}
        if semgrep_mode:
            path = os.path.join(d, "semgrep.json")
            try:
                with open(path) as f:
                    data = json.loads(f.read())
                n = len(data.get("results", [])) if isinstance(data, dict) else 0
                counts["semgrep.json"] = n
            except (OSError, json.JSONDecodeError):
                counts["semgrep.json"] = 0
        else:
            cache_dir = os.path.join(d, CACHE_REL)
            for filename in CACHE_CHECK_FILES:
                path = os.path.join(cache_dir, filename)
                try:
                    with open(path) as f:
                        data = json.loads(f.read())
                    counts[filename] = len(data) if isinstance(data, (dict, list)) else 0
                except (OSError, json.JSONDecodeError):
                    counts[filename] = 0
        if any(v > 0 for v in counts.values()):
            results[d] = counts
    return results


def print_scanned_status(root_dir, all_dirs, scanned, semgrep_mode=False):
    """Print a table showing scan coverage with counts per directory."""
    n_done = len(scanned)
    n_total = len(all_dirs)

    # Precompute display paths so we can size the column dynamically
    display_paths = []
    for d in all_dirs:
        rel = os.path.relpath(d, root_dir)
        display_paths.append("./" if rel == "." else f"./{rel}/")

    dir_col = max((len(p) for p in display_paths), default=9)
    dir_col = max(dir_col, len("Directory"))

    print(f"Scan status: {n_done}/{n_total} director{'y' if n_total == 1 else 'ies'} already have data")
    print()
    if semgrep_mode:
        print(f"  {'':2} {'Directory':<{dir_col}} {'semgrep results':>16}")
        print(f"  {'':2} {'─' * dir_col} {'─' * 16}")
        for d, rel in zip(all_dirs, display_paths):
            counts = scanned.get(d)
            if counts:
                sr = counts.get("semgrep.json", 0)
                print(f"  ✓  {rel:<{dir_col}} {sr:>16,}")
            else:
                print(f"     {rel:<{dir_col}} {'—':>16}")
    else:
        print(f"  {'':2} {'Directory':<{dir_col}} {'function_calls':>14}  {'functions_html':>14}")
        print(f"  {'':2} {'─' * dir_col} {'─' * 14}  {'─' * 14}")
        for d, rel in zip(all_dirs, display_paths):
            counts = scanned.get(d)
            if counts:
                fc = counts.get("function_calls.json", 0)
                fh = counts.get("functions_html.json", 0)
                print(f"  ✓  {rel:<{dir_col}} {fc:>14,}  {fh:>14,}")
            else:
                print(f"     {rel:<{dir_col}} {'—':>14}  {'—':>14}")
    print()


def print_split_commands(root_dir, depth, docker_mode=False, parallelism=3, skip_scanned=False, do_copy=False, run=False, semgrep_mode=False):
    """
    Print xargs-ready scan commands for directories at `depth` levels below root_dir.
    The xargs block appears first; the summary is printed at the bottom.
    """
    split_dirs = get_dirs_at_depth(root_dir, depth)

    if not split_dirs:
        print(f"No directories found at depth {depth} under {root_dir}")
        return

    # Relative paths for display
    rel_dirs = [os.path.relpath(d, root_dir) for d in split_dirs]

    # Per-subdir docker commands
    docker_commands = []
    for d, rel in zip(split_dirs, rel_dirs):
        label_safe = rel.replace("/", "_").replace(".", "_")
        log_file = f'"{root_dir}/.vscode/extract_{label_safe}.log"'
        if semgrep_mode:
            semgrep_cache = os.path.expanduser("~/.semgrep")
            docker_commands.append(
                f'src_dir="{d}" && cd "$src_dir" && echo "[$(date +%H:%M:%S)] START {rel}" && docker run --rm '
                f'-v $(pwd):/app/output '
                f'-v "$src_dir":"$src_dir" '
                f'-v "{semgrep_cache}":/root/.semgrep '
                f'alecmaly/sa-tool semgrep scan --exclude sg-rules --json '
                f'--config ../sg-rules --config auto '
                f'--json-output=semgrep.json --no-git-ignore '
                f'2>&1 | tee {log_file} && echo "[$(date +%H:%M:%S)] DONE {rel}" || echo "[$(date +%H:%M:%S)] FAIL {rel}"'
            )
        else:
            docker_commands.append(
                f'src_dir="{d}" && cd "$src_dir" && echo "[$(date +%H:%M:%S)] START {rel}" && docker run --rm '
                f'-v $(pwd):/app/output '
                f'-v "$(pwd)/.gradle":/root/.gradle '
                f'-v "$src_dir":"$src_dir" '
                f'alecmaly/sa-tool python3 /app/1_extract_w_lsp.py '
                f'-d "$src_dir" -l all 2>&1 | tee {log_file} && echo "[$(date +%H:%M:%S)] DONE {rel}" || echo "[$(date +%H:%M:%S)] FAIL {rel}"'
            )

    # Associate each command with its source directory for skip filtering
    dir_cmds = list(zip(split_dirs, docker_commands))
    all_dirs_ordered = list(split_dirs)

    # Apply skip-scanned filtering
    scanned = {}
    if skip_scanned:
        scanned = check_scanned_dirs(all_dirs_ordered, semgrep_mode=semgrep_mode)
        dir_cmds = [(d, cmd) for d, cmd in dir_cmds if d not in scanned]

    all_docker = [cmd for _, cmd in dir_cmds]
    active_split_dirs = [d for d, _ in dir_cmds]
    subdir_args = " ".join(f'"{d}"' for d in active_split_dirs)

    print("=== Split-Depth Scan ===")
    print(f"Scanning: {root_dir}")
    print(f"Split depth: {depth}  ({len(split_dirs)} sub-dirs)")
    if skip_scanned and scanned:
        n_skip = len(scanned)
        print(f"Skipping {n_skip} already-scanned director{'y' if n_skip == 1 else 'ies'} (see status below)")
    print()

    if not all_docker:
        print("All directories already scanned — nothing to do.")
        print()
    else:
        if semgrep_mode:
            print("Full pipeline (parallel semgrep scan → consolidate):")
        else:
            print("Full pipeline (parallel extract → consolidate → postprocess):")
        print()
        xargs_lines = [
            f"cat <<'JOBS' | xargs -P {parallelism} -I {{}} bash -c '{{}}'",
            *all_docker,
            "JOBS",
        ]
        xargs_block = "\n".join(xargs_lines)

        print("```bash")
        if semgrep_mode:
            print(f"# Step 1: Semgrep scan (parallel, {parallelism} at a time)")
        else:
            print(f"# Step 1: Extract (parallel, {parallelism} at a time)")
        print(xargs_block)
        print()
        print("# Step 2: Consolidate sub-project outputs into root")
        if semgrep_mode:
            print(
                f'src_dir="{root_dir}" && docker run --rm '
                f'-v $(pwd):/app/output '
                f'-v "$src_dir":"$src_dir" '
                f'alecmaly/sa-tool python3 /app/consolidate_outputs.py '
                f'-d "$src_dir" --subdirs {subdir_args} --semgrep'
            )
        else:
            print(
                f'src_dir="{root_dir}" && docker run --rm '
                f'-v $(pwd):/app/output '
                f'-v "$src_dir":"$src_dir" '
                f'alecmaly/sa-tool python3 /app/consolidate_outputs.py '
                f'-d "$src_dir" --subdirs {subdir_args}'
            )
        if not semgrep_mode:
            print()
            print("# Step 3: Postprocess (callstacks, sqlite, decorators)")
            print(
                f'cd "{root_dir}" && src_dir=`pwd` && docker run --rm '
                f'-v $(pwd):/app/output '
                f'-v "$src_dir":"$src_dir" '
                f'alecmaly/sa-tool /bin/bash /app/_process_static_analysis.sh'
            )
        print("```")
        print()

        if do_copy:
            if copy_to_clipboard(xargs_block):
                print("(xargs block copied to clipboard)")
            else:
                print("(copy failed — install xclip/xsel or use a terminal with OSC 52 support)", file=sys.stderr)
            print()

    # Summary at bottom
    print(f"Split directories ({len(split_dirs)}) at depth {depth}:")
    for d in split_dirs:
        rel = os.path.relpath(d, root_dir)
        print(f"  ./{rel}/")
    print()

    if skip_scanned:
        print_scanned_status(root_dir, all_dirs_ordered, scanned, semgrep_mode=semgrep_mode)

    if not run or not active_split_dirs:
        return

    # ── Execute in parallel (mirrors run_pipeline logic) ─────────────────────
    from concurrent.futures import ThreadPoolExecutor

    total = len(active_split_dirs)
    vscode_dir = os.path.join(root_dir, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)

    labels = {}
    for d in active_split_dirs:
        rel = os.path.relpath(d, root_dir)
        labels[d] = rel if rel != "." else "(root)"

    lock = threading.Lock()
    status = {d: "pending" for d in active_split_dirs}
    start_times = {}
    end_times = {}

    def _run_one(d):
        label_safe = labels[d].replace("/", "_").replace(".", "_")
        log_path = os.path.join(vscode_dir, f"extract_{label_safe}.log")
        with lock:
            status[d] = "running"
            start_times[d] = time.time()
        cmd = _build_semgrep_cmd(d) if semgrep_mode else _build_docker_cmd(d)
        try:
            with open(log_path, "w") as log_f:
                proc = subprocess.run(
                    ["bash", "-c", cmd],
                    stdout=log_f, stderr=subprocess.STDOUT,
                    cwd=d,
                )
            with lock:
                end_times[d] = time.time()
                status[d] = "done" if proc.returncode == 0 else "FAILED"
        except Exception:
            with lock:
                end_times[d] = time.time()
                status[d] = "FAILED"

    def _progress_printer():
        while True:
            time.sleep(5)
            with lock:
                n_done = sum(1 for s in status.values() if s in ("done", "FAILED"))
                n_run = sum(1 for s in status.values() if s == "running")
                n_fail = sum(1 for s in status.values() if s == "FAILED")
            elapsed_parts = []
            for d in active_split_dirs:
                with lock:
                    if status[d] == "running" and d in start_times:
                        secs = int(time.time() - start_times[d])
                        elapsed_parts.append(f"{labels[d]} ({secs}s)")
            ts = time.strftime("%H:%M:%S")
            line = f"  [{ts}]  {n_done}/{total} done"
            if n_fail:
                line += f" ({n_fail} failed)"
            line += f",  {n_run} running"
            if elapsed_parts:
                line += f":  {', '.join(elapsed_parts)}"
            print(line, flush=True)
            if n_done == total:
                break

    scan_label = "Semgrep scanning" if semgrep_mode else "Extracting"
    print(f"\n{'=' * 60}")
    print(f"  {scan_label} ({total} sub-dirs, {parallelism} parallel)")
    print(f"{'=' * 60}\n")

    monitor = threading.Thread(target=_progress_printer, daemon=True)
    monitor.start()

    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        futures = [pool.submit(_run_one, d) for d in active_split_dirs]
        for f in futures:
            f.result()

    monitor.join(timeout=10)

    failed = [d for d, s in status.items() if s == "FAILED"]
    succeeded = [d for d, s in status.items() if s == "done"]
    complete_label = "Semgrep scan" if semgrep_mode else "Extraction"
    print(f"\n  {complete_label} complete: {len(succeeded)} succeeded, {len(failed)} failed")
    for d in failed:
        label_safe = labels[d].replace("/", "_").replace(".", "_")
        log_path = os.path.join(vscode_dir, f"extract_{label_safe}.log")
        print(f"    FAILED: {labels[d]}  (log: {log_path})")

    total_time = max(end_times.values()) - min(start_times.values()) if start_times else 0
    subdir_args = " ".join(f'"{d}"' for d in active_split_dirs)
    semgrep_flag = " --semgrep" if semgrep_mode else ""
    print(f"\n{'=' * 60}")
    print(f"  {complete_label} complete  ({int(total_time)}s)")
    print(f"  Logs: {vscode_dir}/extract_*.log")
    print()
    print(f"  Next steps:")
    print(f"    # Step 2: Consolidate")
    print(
        f'    src_dir="{root_dir}" && docker run --rm '
        f'-v $(pwd):/app/output '
        f'-v "$src_dir":"$src_dir" '
        f'alecmaly/sa-tool python3 /app/consolidate_outputs.py '
        f'-d "$src_dir" --subdirs {subdir_args}{semgrep_flag}'
    )
    if not semgrep_mode:
        print()
        print(f"    # Step 3: Postprocess")
        print(
            f'    cd "{root_dir}" && src_dir=`pwd` && docker run --rm '
            f'-v $(pwd):/app/output '
            f'-v "$src_dir":"$src_dir" '
            f'alecmaly/sa-tool /bin/bash /app/_process_static_analysis.sh'
        )
    print(f"{'=' * 60}\n")


# ──────────────────────────────────────────────────────────────────────────────
# Step 4: Output — table, commands, or JSON
# ──────────────────────────────────────────────────────────────────────────────

def emit_json(root_dir, recommendations, output_path=None):
    """
    Emit structured JSON for LLM or programmatic evaluation.

    Each root includes hierarchy info (parent/children) so an LLM can
    reason about which roots are redundant vs. which represent unique
    sub-projects that need their own scan.
    """
    data = {
        "scan_dir": root_dir,
        "languages": [],
    }

    for rec in recommendations:
        lang_entry = {
            "language": rec["language"],
            "lsp_workspace_support": LSP_HANDLES_MONOREPO.get(rec["language"], "none"),
            "strategy": rec["strategy"],
            "note": rec["note"],
            "roots": [],
        }
        for root in rec["roots"]:
            rel = os.path.relpath(root["dir"], root_dir)
            if rel == ".":
                rel = "./"
            else:
                rel = f"./{rel}/"

            parent_rel = None
            if root.get("parent"):
                parent_rel = os.path.relpath(root["parent"], root_dir)
                parent_rel = "./" if parent_rel == "." else f"./{parent_rel}/"

            children_rel = []
            for c in root.get("children", []):
                cr = os.path.relpath(c, root_dir)
                children_rel.append("./" if cr == "." else f"./{cr}/")

            lang_entry["roots"].append({
                "dir": root["dir"],
                "relative": rel,
                "marker": root["marker"],
                "files": root["files"],
                "is_workspace": root["is_workspace"],
                "parent": parent_rel,
                "children": children_rel,
            })

        data["languages"].append(lang_entry)

    json_str = json.dumps(data, indent=2)
    if output_path:
        with open(output_path, "w") as f:
            f.write(json_str)
        print(f"JSON written to {output_path}", file=sys.stderr)
    else:
        print(json_str)


def print_results(root_dir, recommendations, docker_mode=False, skip_scanned=False, do_copy=False, semgrep_mode=False, no_partition_csharp=False, csharp_groups=None, chunk_size=2000):
    """Print detection table and generate scan commands."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    extract_script = os.path.join(script_dir, "1_extract_w_lsp.py")

    print("=== Project Root Detection ===")
    print(f"Scanning: {root_dir}")
    print()

    if not recommendations:
        print("No project roots detected.")
        return

    # Collect unique scan root directories across all languages
    scan_dirs = []
    seen_dirs = set()
    dir_to_languages = {}  # track which languages each dir is associated with
    for rec in recommendations:
        for root in get_scan_roots(rec):
            d = root["dir"]
            dir_to_languages.setdefault(d, set()).add(rec["language"])
            if d not in seen_dirs:
                seen_dirs.add(d)
                scan_dirs.append(d)

    all_scan_dirs = list(scan_dirs)  # preserve full list for status display

    # Apply skip-scanned filtering
    scanned = {}
    if skip_scanned:
        scanned = check_scanned_dirs(all_scan_dirs, semgrep_mode=semgrep_mode)
        scan_dirs = [d for d in scan_dirs if d not in scanned]
        if scanned:
            n_skip = len(scanned)
            print(f"Skipping {n_skip} already-scanned director{'y' if n_skip == 1 else 'ies'} (see status below)")
            print()

    # Build lookup for solution roots (C# solution strategy)
    sln_roots = {}
    csharp_partition_groups = None  # Set if partitioning is active

    has_csharp_solution = any(rec["strategy"] == "solution" for rec in recommendations)
    if has_csharp_solution and not no_partition_csharp:
        # Step 0: Set up C# project for OmniSharp (fix csproj refs, create sln, Directory.Build.props)
        try:
            sln_root = None
            for rec in recommendations:
                if rec["strategy"] == "solution":
                    sln_root = _find_solution_root(rec)
                    break

            if sln_root:
                # Check if sln already exists — skip setup if so
                existing_sln = [f for f in os.listdir(sln_root) if f.endswith('.sln') and not f.startswith('group_')]
                if not existing_sln:
                    print("  Setting up C# project for OmniSharp...")
                    _run_fix_csproj_for_lsp(sln_root)
                else:
                    print(f"  C# project already set up ({existing_sln[0]} exists)")
        except Exception as e:
            print(f"  Warning: C# project setup failed: {e}")

        # Use locally-defined partition logic
        try:
            # Find the C# solution root (may have been created by fix_csproj above)
            if sln_root is None:
                for rec in recommendations:
                    if rec["strategy"] == "solution":
                        sln_root = _find_solution_root(rec)
                        break

            if sln_root:
                print(f"\n{'=' * 60}")
                print(f"  C# PARTITION PLAN")
                print(f"{'=' * 60}")

                deps, csproj_paths = parse_dependency_graph(sln_root)
                file_counts = count_files(sln_root)
                total_files = sum(file_counts.values())
                print(f"  {len(deps)} projects, {total_files} .cs files")

                print(f"  Chunk size target: {chunk_size} files")

                large = detect_large_projects(file_counts, chunk_size=chunk_size)

                split_projects = {}
                if large:
                    print(f"\n  Large projects (auto-split by subdirectory):")
                for proj_name, n_chunks in large.items():
                    subdirs = enumerate_project_subdirs(sln_root, proj_name)
                    if len(subdirs) >= n_chunks:
                        chunks, chunk_sizes_list = split_large_project(subdirs, n_chunks)
                        split_projects[proj_name] = (chunks, chunk_sizes_list)
                        print(f"    {proj_name}: {file_counts[proj_name]} files -> {n_chunks} chunks")
                        for ci, (chunk, size) in enumerate(zip(chunks, chunk_sizes_list)):
                            top3 = ', '.join(f'{n}({c})' for c, n in chunk[:3])
                            print(f"      Chunk {ci}: {size} files, {len(chunk)} subdirs [{top3}, ...]")

                groups = partition_projects(deps, file_counts, split_projects, chunk_size=chunk_size)
                n_groups = len(groups)

                # Compute sln sets and generate .sln files + include regexes
                all_projects = set(deps.keys())
                csharp_partition_groups = []

                # All chunks share the same master .sln for cross-project resolution
                master_sln_name = [f for f in os.listdir(sln_root) if f.endswith('.sln') and not f.startswith('group_')]
                if master_sln_name:
                    master_sln_path = os.path.join(sln_root, master_sln_name[0])
                else:
                    # Shouldn't happen (created by _run_fix_csproj_for_lsp), but just in case
                    master_sln_path = os.path.join(sln_root, os.path.basename(sln_root) + '.sln')
                print(f"  Master .sln: {os.path.basename(master_sln_path)} ({len(all_projects)} projects)")

                print(f"\n  Partitioning into {n_groups} chunks (~{chunk_size} files each):")
                max_group_files = 0
                for i, group in enumerate(groups):
                    sln_projects = compute_sln_projects(group, deps, all_projects)
                    include_regex = build_include_regex(group)
                    cache_dir = os.path.join(sln_root, f"scan_group_{i}", ".vscode", "ext-static-analysis", "cache")

                    # Create per-group .sln with only this group's transitive deps
                    # (smaller sln = less RAM per OmniSharp instance, ~5-8GB vs ~20GB)
                    group_sln_path = os.path.join(sln_root, f"group_{i}.sln")
                    write_sln(group_sln_path, sln_projects, csproj_paths)

                    csharp_partition_groups.append({
                        'index': i,
                        'sln_path': group_sln_path,
                        'sln_root': sln_root,
                        'sln_projects': sln_projects,
                        'csproj_paths': csproj_paths,
                        'include_regex': include_regex,
                        'cache_dir': cache_dir,
                        'total_files': group['total_files'],
                        'scan_projects': group['scan_projects'],
                        'split_chunks': group.get('split_chunks', []),
                    })
                    max_group_files = max(max_group_files, group['total_files'])

                    scan_count = len(group['scan_projects']) + len(group.get('split_chunks', []))
                    print(f"    Chunk {i}: {group['total_files']} files, {scan_count} targets, "
                          f"{len(sln_projects)} projects in .sln")

                    # Top 3 largest targets
                    scan_sizes = sorted([(file_counts.get(p, 0), p) for p in group['scan_projects']], reverse=True)
                    for proj_name, chunk_idx, subdirs in group.get('split_chunks', []):
                        if proj_name in split_projects:
                            _, chunk_sizes_local = split_projects[proj_name]
                            if chunk_idx < len(chunk_sizes_local):
                                scan_sizes.insert(0, (chunk_sizes_local[chunk_idx], f"{proj_name}[chunk {chunk_idx}]"))
                    for count, name in scan_sizes[:3]:
                        print(f"      {count:>6} {name}")

                total_csharp_files = sum(g['total_files'] for g in csharp_partition_groups)
                ram_est = n_groups * 8

                print(f"\n  Estimates:")
                for rate in [8, 12, 17]:
                    init_est = max(len(g.get('sln_projects', set())) for g in csharp_partition_groups) * 0.05
                    wall_hr = (max_group_files / rate + init_est) / 60
                    print(f"    At {rate:>2} files/min: ~{wall_hr:.1f}h wall clock")
                print(f"    RAM: ~{ram_est}GB ({n_groups} x ~8GB per instance)")
                print(f"{'=' * 60}\n")

        except Exception as e:
            print(f"  Warning: C# partition failed: {e}, falling back to per-project scanning")
            csharp_partition_groups = None

    # Fall back to old per-project solution roots if not partitioning
    if csharp_partition_groups is None:
        for rec in recommendations:
            if rec["strategy"] == "solution":
                sln_root = _find_solution_root(rec)
                if sln_root:
                    for root in get_scan_roots(rec):
                        sln_roots[root["dir"]] = sln_root

    if scan_dirs or csharp_partition_groups:
        # Build commands — docker by default, local only with --no-docker
        docker_commands = []
        install_commands = []
        local_commands = []

        # C# partition groups (replaces per-project C# commands)
        if csharp_partition_groups:
            # All chunks share the master .sln — just create output dirs
            for g in csharp_partition_groups:
                os.makedirs(g['cache_dir'], exist_ok=True)

            for g in csharp_partition_groups:
                label = f"csharp_group_{g['index']}"
                log_file = f'"{root_dir}/.vscode/extract_{label}.log"'
                docker_commands.append(
                    f'echo "[$(date +%H:%M:%S)] START {label} ({g["total_files"]} files)" && docker run --rm '
                    f'-v "{g["sln_root"]}":/app/output '
                    f'-v "{g["sln_root"]}":"{g["sln_root"]}" '
                    f'alecmaly/sa-tool python3 /app/1_extract_w_lsp.py '
                    f'-d "{g["sln_root"]}" -l "c#" '
                    f'--include-paths "{g["include_regex"]}" '
                    f'-o "{g["cache_dir"]}/" '
                    f'--cmd-override "OmniSharp -s {g["sln_path"]} --stdio" '
                    f'2>&1 | tee {log_file} && echo "[$(date +%H:%M:%S)] DONE {label}" || echo "[$(date +%H:%M:%S)] FAIL {label}"'
                )

        # Build set of C# dirs to skip when partitioning is active
        csharp_partitioned_dirs = set()
        if csharp_partition_groups:
            for rec in recommendations:
                if rec["strategy"] == "solution":
                    for root in get_scan_roots(rec):
                        csharp_partitioned_dirs.add(root["dir"])

        # Non-C# scan dirs (and C# dirs if not partitioning)
        for d in scan_dirs:
            # Skip C# dirs if partitioning is active (they're handled above)
            if d in csharp_partitioned_dirs:
                continue

            label = os.path.relpath(d, root_dir) or "root"
            label_safe = label.replace("/", "_").replace(".", "_")
            log_file = f'"{root_dir}/.vscode/extract_{label_safe}.log"'

            if semgrep_mode:
                semgrep_cache = os.path.expanduser("~/.semgrep")
                docker_commands.append(
                    f'src_dir="{d}" && cd "$src_dir" && echo "[$(date +%H:%M:%S)] START {label}" && docker run --rm '
                    f'-v $(pwd):/app/output '
                    f'-v "$src_dir":"$src_dir" '
                    f'-v "{semgrep_cache}":/root/.semgrep '
                    f'alecmaly/sa-tool semgrep scan --exclude sg-rules --json '
                    f'--config ../sg-rules --config auto '
                    f'--json-output=semgrep.json --no-git-ignore '
                    f'2>&1 | tee {log_file} && echo "[$(date +%H:%M:%S)] DONE {label}" || echo "[$(date +%H:%M:%S)] FAIL {label}"'
                )
            elif d in sln_roots:
                # C# solution strategy (non-partitioned fallback)
                sln_root = sln_roots[d]
                proj_name = os.path.basename(d)
                cache_dir = os.path.join(d, ".vscode", "ext-static-analysis", "cache")
                docker_commands.append(
                    f'echo "[$(date +%H:%M:%S)] START {label}" && docker run --rm '
                    f'-v "{d}":/app/output '
                    f'-v "{sln_root}":"{sln_root}" '
                    f'alecmaly/sa-tool python3 /app/1_extract_w_lsp.py '
                    f'-d "{sln_root}" -l "c#" '
                    f'--include-paths "{proj_name}/" '
                    f'-o "{cache_dir}/" '
                    f'2>&1 | tee {log_file} && echo "[$(date +%H:%M:%S)] DONE {label}" || echo "[$(date +%H:%M:%S)] FAIL {label}"'
                )
            else:
                docker_commands.append(
                    f'src_dir="{d}" && cd "$src_dir" && echo "[$(date +%H:%M:%S)] START {label}" && docker run --rm '
                    f'-v $(pwd):/app/output '
                    f'-v "$(pwd)/.gradle":/root/.gradle '
                    f'-v "$src_dir":"$src_dir" '
                    f'alecmaly/sa-tool python3 /app/1_extract_w_lsp.py '
                    f'-d "$src_dir" -l all 2>&1 | tee {log_file} && echo "[$(date +%H:%M:%S)] DONE {label}" || echo "[$(date +%H:%M:%S)] FAIL {label}"'
                )
            local_commands.append(
                f'cd "{d}" && python {extract_script} -d "{d}" -l all'
            )

        consolidate_script = os.path.join(script_dir, "consolidate_outputs.py")

        # Emit full pipeline as a copy-pasteable script block
        xargs_lines = [
            "cat <<'JOBS' | xargs -P 3 -I {} bash -c '{}'",
            *docker_commands,
            "JOBS",
        ]
        xargs_block = "\n".join(xargs_lines)

        if semgrep_mode:
            print("Full pipeline (parallel semgrep scan → consolidate):")
        else:
            print("Full pipeline (parallel extract → consolidate → postprocess):")
        print()
        print("```bash")

        # Collect install commands — skip any install dir that sits under an
        # already-scanned root (same rule as run_pipeline below).
        skipped_set = set(scanned) if scanned else set()
        install_commands = []
        for d, lang, install_cmd in get_install_roots(recommendations):
            if _is_under_skipped(d, skipped_set) or lang == "c#":
                continue
            label = os.path.relpath(d, root_dir) or "root"
            install_commands.append(
                f'src_dir="{d}" && cd "$src_dir" && echo "[$(date +%H:%M:%S)] INSTALL ({lang}) {label}" && '
                f'docker run --rm -v "$src_dir":"$src_dir" -w "$src_dir" alecmaly/sa-tool '
                f'sh -c \'{install_cmd}\' && echo "[$(date +%H:%M:%S)] INSTALL DONE {label}" || echo "[$(date +%H:%M:%S)] INSTALL FAIL {label} (non-fatal)"'
            )

        # Emit install step if any deps needed
        if install_commands and not semgrep_mode:
            install_xargs_lines = [
                "cat <<'JOBS' | xargs -P 3 -I {} bash -c '{}'",
                *install_commands,
                "JOBS",
            ]
            print("# Step 0 (optional): Install dependencies for LSP resolution")
            print("\n".join(install_xargs_lines))
            print()

        if semgrep_mode:
            print("# Step 1: Semgrep scan (parallel, 3 at a time)")
        else:
            print("# Step 1: Extract (parallel, 3 at a time)")
        print(xargs_block)
        print()
        print("# Step 2: Consolidate sub-project outputs into root")
        if semgrep_mode:
            if docker_mode:
                print(
                    f'src_dir="{root_dir}" && docker run --rm '
                    f'-v $(pwd):/app/output '
                    f'-v "$src_dir":"$src_dir" '
                    f'alecmaly/sa-tool python3 /app/consolidate_outputs.py '
                    f'-d "$src_dir" --semgrep'
                )
            else:
                print(f'python {consolidate_script} -d "{root_dir}" --semgrep')
        else:
            if docker_mode:
                print(
                    f'src_dir="{root_dir}" && docker run --rm '
                    f'-v $(pwd):/app/output '
                    f'-v "$src_dir":"$src_dir" '
                    f'alecmaly/sa-tool python3 /app/consolidate_outputs.py '
                    f'-d "$src_dir"'
                )
            else:
                print(f'python {consolidate_script} -d "{root_dir}"')
        if not semgrep_mode:
            print()
            print("# Step 3: Postprocess (callstacks, sqlite, decorators)")
            print(
                f'cd "{root_dir}" && src_dir=`pwd` && docker run --rm '
                f'-v $(pwd):/app/output '
                f'-v "$src_dir":"$src_dir" '
                f'alecmaly/sa-tool /bin/bash /app/_process_static_analysis.sh'
            )
        print("```")
        print()

        if do_copy:
            if copy_to_clipboard(xargs_block):
                print("(xargs block copied to clipboard)")
            else:
                print("(copy failed — install xclip/xsel or use a terminal with OSC 52 support)", file=sys.stderr)
            print()
    elif skip_scanned:
        print("All directories already scanned — nothing to do.")
        print()

    # ── Summary at bottom ────────────────────────────────────────────────────
    print("Detected sub-projects:")
    print()
    print(f"  {'Root':<40} {'Language':<12} {'Marker':<25} {'Files':>6}  {'WS':<4} {'Parent'}")
    print(f"  {'─' * 40} {'─' * 12} {'─' * 25} {'─' * 6}  {'─' * 4} {'─' * 20}")

    for rec in recommendations:
        for root in rec["roots"]:
            rel = os.path.relpath(root["dir"], root_dir)
            if rel == ".":
                rel = "./"
            else:
                rel = f"./{rel}/"

            ws_flag = "yes" if root["is_workspace"] else ""

            parent_rel = ""
            if root.get("parent"):
                p = os.path.relpath(root["parent"], root_dir)
                parent_rel = "./" if p == "." else f"./{p}/"

            print(
                f"  {rel:<40} {rec['language']:<12} {root['marker']:<25} {root['files']:>6}  {ws_flag:<4} {parent_rel}"
            )

    print()

    # Notes per language
    for rec in recommendations:
        lang = rec["language"]
        strategy = rec["strategy"]

        if strategy != "single":
            icon = "✓" if strategy == "workspace" else "⚠"
            print(f"{icon} {lang}: {rec['note']}")
            print()

    if skip_scanned:
        print_scanned_status(root_dir, all_scan_dirs, scanned, semgrep_mode=semgrep_mode)


# ──────────────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────────────

def _is_excluded(directory, root_dir, exclude_patterns):
    """
    Check if a detected root should be excluded.

    Matches the relative path (e.g. "packages/legacy-app") against each
    pattern using fnmatch glob syntax.  Both the relative path and a
    trailing-slash variant are tested so that patterns like "packages/*"
    work whether or not the user includes a trailing slash.

    For segment matching (patterns without "/"), plain strings are matched
    as case-insensitive substrings (so "test" excludes "tests", "test-utils",
    etc.), while glob patterns (containing *, ?, []) use fnmatch.

    Special case: "." excludes only the root directory itself.
    """
    if not exclude_patterns:
        return False

    rel = os.path.relpath(directory, root_dir)
    # Normalize to forward slashes for consistent matching
    rel = rel.replace(os.sep, "/")
    candidates = [rel, f"{rel}/"]
    # Also match against individual path segments so that e.g. "templates"
    # excludes "cli/lib/spree_cli/templates/extension"
    segments = rel.split("/")

    for pattern in exclude_patterns:
        pattern = pattern.replace(os.sep, "/")

        # Special case: "." means the root directory itself
        if pattern == ".":
            if rel == ".":
                return True
            continue

        # Full-path match (original behavior)
        for candidate in candidates:
            if fnmatch.fnmatch(candidate, pattern):
                return True
        # Segment match: exclude if any component contains the pattern
        # as a substring (so -x "test" excludes "tests", "test-utils", etc.)
        if "/" not in pattern:
            has_glob = any(c in pattern for c in "*?[]")
            for seg in segments:
                if has_glob:
                    if fnmatch.fnmatch(seg, pattern):
                        return True
                else:
                    if pattern.lower() in seg.lower():
                        return True
    return False


def detect_project_roots(root_dir, languages=None, exclude_patterns=None):
    """
    Main detection pipeline. Returns recommendations list.

    Args:
        root_dir: Directory to scan.
        languages: Optional list of languages to check.
        exclude_patterns: Optional list of fnmatch glob patterns.  Any
            detected root whose relative path matches a pattern is dropped
            before commands are generated.
    """
    root_dir = os.path.abspath(os.path.expanduser(root_dir))
    exclude_patterns = exclude_patterns or []

    if not os.path.isdir(root_dir):
        print(f"Error: {root_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Step 1: Find markers
    markers = find_project_markers(root_dir, languages)

    # Deduplicate
    markers = deduplicate_roots(markers)

    # Step 2: Count source files, drop roots with 0 files
    for m in markers:
        m["files"] = count_source_files(m["dir"], m["language"])

    markers = [m for m in markers if m["files"] > 0]

    # Step 2.5: Apply exclude patterns
    if exclude_patterns:
        before = len(markers)
        markers = [m for m in markers if not _is_excluded(m["dir"], root_dir, exclude_patterns)]
        excluded_count = before - len(markers)
        if excluded_count:
            print(f"Excluded {excluded_count} root(s) matching: {', '.join(exclude_patterns)}", file=sys.stderr)

    # Step 2.5: Compute hierarchy
    markers = compute_hierarchy(markers, root_dir)

    # Step 3: Build recommendations
    recommendations = build_recommendations(root_dir, markers)

    return recommendations


def _build_docker_cmd(d, language=None, solution_root=None, include_paths=None, output_prefix=None):
    """Build the docker run command string for a scan directory (no tee/echo wrapper).

    For C# with a solution root, OmniSharp scans from the solution root but
    filters to only process files matching include_paths, with output written
    to the per-project output_prefix. This gives cross-assembly resolution
    while allowing parallel per-project scanning.
    """
    scan_dir = solution_root or d
    lang_flag = f'-l "{language}"' if language else '-l all'
    include_flag = f'--include-paths "{include_paths}"' if include_paths else ''
    output_flag = f'-o "{output_prefix}"' if output_prefix else ''

    # Mount both solution root and project dir if they differ
    mounts = f'-v "{d}":/app/output -v "{d}":"{d}"'
    if solution_root and solution_root != d:
        mounts = f'-v "{d}":/app/output -v "{solution_root}":"{solution_root}"'

    gradle_mount = f'-v "{d}/.gradle":/root/.gradle' if not language or language != 'c#' else ''

    return (
        f'docker run --rm '
        f'{mounts} '
        f'{gradle_mount} '
        f'alecmaly/sa-tool python3 /app/1_extract_w_lsp.py '
        f'-d "{scan_dir}" {lang_flag} {include_flag} {output_flag}'
    ).replace('  ', ' ').strip()


def _build_semgrep_cmd(d):
    """Build the docker run command string for a semgrep scan directory."""
    semgrep_cache = os.path.expanduser("~/.semgrep")
    os.makedirs(semgrep_cache, exist_ok=True)
    return (
        f'docker run --rm '
        f'-v "{d}":/app/output '
        f'-v "{d}":"{d}" '
        f'-v "{semgrep_cache}":/root/.semgrep '
        f'alecmaly/sa-tool semgrep scan --exclude sg-rules --json '
        f'--config ../sg-rules --config auto '
        f'--json-output=semgrep.json --no-git-ignore'
    )


def run_pipeline(root_dir, recommendations, parallelism=3, skip_scanned=False,
                  semgrep_mode=False, no_partition_csharp=False, csharp_groups=None, chunk_size=2000):
    """
    Execute the extraction step (docker 1_extract_w_lsp.py) for each
    sub-project in parallel with live progress.  Prints the consolidate
    and postprocess commands at the end for manual execution.
    """
    scan_dirs = []
    seen_dirs = set()
    dir_to_languages = {}
    dir_to_solution_root = {}  # C# solution strategy: project_dir -> sln_root
    csharp_partition_cmds = []  # Partition group commands (replace per-project C# scans)

    for rec in recommendations:
        sln_root = _find_solution_root(rec) if rec["strategy"] == "solution" else None
        for root in get_scan_roots(rec):
            d = root["dir"]
            dir_to_languages.setdefault(d, set()).add(rec["language"])
            if sln_root:
                dir_to_solution_root[d] = sln_root
            if d not in seen_dirs:
                seen_dirs.add(d)
                scan_dirs.append(d)

    # C# partitioning: replace per-project C# scans with group scans
    if not no_partition_csharp and dir_to_solution_root:
        try:
            sln_root = next(iter(dir_to_solution_root.values()))
            deps, csproj_paths = parse_dependency_graph(sln_root)
            file_counts_map = count_files(sln_root)

            large = detect_large_projects(file_counts_map, chunk_size=chunk_size)

            split_projects = {}
            for proj_name, n_chunks in large.items():
                subdirs = enumerate_project_subdirs(sln_root, proj_name)
                if len(subdirs) >= n_chunks:
                    chunks, chunk_sizes_list = split_large_project(subdirs, n_chunks)
                    split_projects[proj_name] = (chunks, chunk_sizes_list)
                    print(f"    Auto-splitting {proj_name} into {n_chunks} chunks")

            groups = partition_projects(deps, file_counts_map, split_projects, chunk_size=chunk_size)
            n_groups = len(groups)
            print(f"  C# partition: built {n_groups} chunks (~{chunk_size} files each)")
            all_projects = set(deps.keys())

            # Find master .sln — all chunks share it for cross-project resolution
            master_sln_name = [f for f in os.listdir(sln_root) if f.endswith('.sln') and not f.startswith('group_')]
            master_sln_path = os.path.join(sln_root, master_sln_name[0]) if master_sln_name else os.path.join(sln_root, os.path.basename(sln_root) + '.sln')

            # Generate output dirs and build commands
            for i, group in enumerate(groups):
                include_regex = build_include_regex(group)
                cache_dir = os.path.join(sln_root, f"scan_group_{i}", ".vscode", "ext-static-analysis", "cache")

                os.makedirs(cache_dir, exist_ok=True)

                csharp_partition_cmds.append({
                    'label': f"csharp_group_{i}",
                    'sln_root': sln_root,
                    'sln_path': master_sln_path,
                    'include_regex': include_regex,
                    'cache_dir': cache_dir,
                    'total_files': group['total_files'],
                })

            # Remove C# dirs from scan_dirs (handled by partition groups)
            csharp_dirs = set(dir_to_solution_root.keys())
            scan_dirs = [d for d in scan_dirs if d not in csharp_dirs]
            dir_to_solution_root = {}

            print(f"    Generated {len(csharp_partition_cmds)} partition groups")
        except Exception as e:
            print(f"  Warning: C# partition failed: {e}, falling back to per-project C# scanning")

    scanned = set()
    if skip_scanned:
        scanned = set(check_scanned_dirs(scan_dirs, semgrep_mode=semgrep_mode))
        n_skip = len(scanned)
        scan_dirs = [d for d in scan_dirs if d not in scanned]
        if n_skip:
            print(f"Skipping {n_skip} already-scanned director{'y' if n_skip == 1 else 'ies'}")

    # Add partition groups as virtual scan targets (skip already-scanned ones)
    partition_scan_ids = []
    for pg in csharp_partition_cmds:
        scan_id = f"__partition__{pg['label']}"
        if skip_scanned:
            # Check if this group's output already has data
            cache_dir = pg['cache_dir']
            has_data = False
            for check_file in CACHE_CHECK_FILES:
                path = os.path.join(cache_dir, check_file)
                try:
                    with open(path) as f:
                        data = json.loads(f.read())
                    if isinstance(data, (dict, list)) and len(data) > 0:
                        has_data = True
                        break
                except (OSError, json.JSONDecodeError):
                    pass
            if has_data:
                print(f"Skipping already-scanned {pg['label']}")
                continue
        partition_scan_ids.append(scan_id)
        scan_dirs.append(scan_id)

    if not scan_dirs:
        print("No sub-projects to extract.")
        return

    total = len(scan_dirs)
    labels = {}
    for d in scan_dirs:
        if d.startswith("__partition__"):
            labels[d] = d.replace("__partition__", "")
        else:
            rel = os.path.relpath(d, root_dir)
            labels[d] = rel if rel != "." else "(root)"

    # Ensure .vscode dir exists and is writable for log files.
    # Docker containers run as root and may have created this dir with root ownership.
    vscode_dir = os.path.join(root_dir, ".vscode")
    os.makedirs(vscode_dir, exist_ok=True)
    if not os.access(vscode_dir, os.W_OK):
        print(f"Warning: {vscode_dir} is not writable (owned by root from Docker?)")
        print(f"  Fix with: docker run --rm -v \"{root_dir}\":/data alecmaly/sa-tool chown -R {os.getuid()}:{os.getgid()} /data/.vscode")
        try:
            subprocess.run(
                ["docker", "run", "--rm", "-v", f"{root_dir}:/data",
                 "alecmaly/sa-tool", "chown", "-R", f"{os.getuid()}:{os.getgid()}", "/data/.vscode"],
                capture_output=True, timeout=10
            )
        except Exception:
            pass

    # ── Step 0: Install dependencies (sequential, before parallel scan) ──
    if not semgrep_mode:
        install_needed = [
            (d, lang, cmd) for d, lang, cmd in get_install_roots(recommendations)
            if not _is_under_skipped(d, scanned) and lang != "c#"
        ]

        if install_needed:
            print(f"\n{'=' * 60}")
            print(f"  Installing dependencies ({len(install_needed)} projects)")
            print(f"{'=' * 60}\n")
            for d, lang, install_cmd in install_needed:
                label = labels.get(d, os.path.relpath(d, root_dir))
                print(f"  [{time.strftime('%H:%M:%S')}] INSTALL ({lang}) {label}")
                docker_install = (
                    f'docker run --rm -v "{d}":"{d}" -w "{d}" '
                    f'alecmaly/sa-tool sh -c \'{install_cmd}\''
                )
                proc = subprocess.run(
                    ["bash", "-c", docker_install],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    cwd=d,
                )
                result = "done" if proc.returncode == 0 else "failed (non-fatal)"
                print(f"  [{time.strftime('%H:%M:%S')}] INSTALL {result}: {label}")

    # ── Step 1: Parallel extraction / semgrep scan ──────────────────────
    scan_label = "Semgrep scanning" if semgrep_mode else "Extracting"
    print(f"\n{'=' * 60}")
    print(f"  {scan_label} ({total} sub-projects, {parallelism} parallel)")
    print(f"{'=' * 60}\n")

    lock = threading.Lock()
    status = {}         # dir -> "pending" | "running" | "done" | "FAILED"
    start_times = {}
    end_times = {}

    for d in scan_dirs:
        status[d] = "pending"

    def _run_one(d):
        label = labels[d]
        label_safe = label.replace("/", "_").replace(".", "_")
        log_path = os.path.join(vscode_dir, f"extract_{label_safe}.log")

        with lock:
            status[d] = "running"
            start_times[d] = time.time()

        if d.startswith("__partition__"):
            # C# partition group — virtual entry, not a real directory
            pg_label = d.replace("__partition__", "")
            pg = next(pg for pg in csharp_partition_cmds if pg['label'] == pg_label)
            run_cwd = pg["sln_root"]  # Use sln root as working directory
            cmd = (
                f'docker run --rm '
                f'-v "{pg["sln_root"]}":/app/output '
                f'-v "{pg["sln_root"]}":"{pg["sln_root"]}" '
                f'alecmaly/sa-tool python3 /app/1_extract_w_lsp.py '
                f'-d "{pg["sln_root"]}" -l "c#" '
                f'--include-paths "{pg["include_regex"]}" '
                f'-o "{pg["cache_dir"]}/" '
                f'--cmd-override "OmniSharp -s {pg["sln_path"]} --stdio"'
            )
        elif semgrep_mode:
            run_cwd = d
            cmd = _build_semgrep_cmd(d)
        elif d in dir_to_solution_root:
            # C# solution strategy (non-partitioned fallback)
            run_cwd = d
            sln_root = dir_to_solution_root[d]
            proj_name = os.path.basename(d)
            cache_dir = os.path.join(d, ".vscode", "ext-static-analysis", "cache")
            os.makedirs(cache_dir, exist_ok=True)
            cmd = _build_docker_cmd(
                d, language="c#",
                solution_root=sln_root,
                include_paths=f"{proj_name}/",
                output_prefix=f"{cache_dir}/",
            )
        else:
            run_cwd = d
            cmd = _build_docker_cmd(d)
        try:
            with open(log_path, "w") as log_f:
                proc = subprocess.run(
                    ["bash", "-c", cmd],
                    stdout=log_f, stderr=subprocess.STDOUT,
                    cwd=run_cwd,
                )
            with lock:
                end_times[d] = time.time()
                status[d] = "done" if proc.returncode == 0 else "FAILED"
        except Exception as e:
            with lock:
                end_times[d] = time.time()
                status[d] = "FAILED"

    def _progress_printer():
        """Print a periodic status line until all jobs finish."""
        while True:
            time.sleep(5)
            with lock:
                n_done = sum(1 for s in status.values() if s in ("done", "FAILED"))
                n_run = sum(1 for s in status.values() if s == "running")
                n_fail = sum(1 for s in status.values() if s == "FAILED")
                running_names = [
                    labels[d] for d, s in status.items() if s == "running"
                ]

            elapsed_parts = []
            for d in scan_dirs:
                with lock:
                    if status[d] == "running" and d in start_times:
                        secs = int(time.time() - start_times[d])
                        elapsed_parts.append(f"{labels[d]} ({secs}s)")

            ts = time.strftime("%H:%M:%S")
            line = f"  [{ts}]  {n_done}/{total} done"
            if n_fail:
                line += f" ({n_fail} failed)"
            line += f",  {n_run} running"
            if elapsed_parts:
                line += f":  {', '.join(elapsed_parts)}"
            print(line, flush=True)

            if n_done == total:
                break

    monitor = threading.Thread(target=_progress_printer, daemon=True)
    monitor.start()

    # Run extraction jobs using a thread pool
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=parallelism) as pool:
        futures = [pool.submit(_run_one, d) for d in scan_dirs]
        for f in futures:
            f.result()  # wait for all

    monitor.join(timeout=10)

    # Final summary
    print()
    failed = [d for d, s in status.items() if s == "FAILED"]
    succeeded = [d for d, s in status.items() if s == "done"]
    complete_label = "Semgrep scan" if semgrep_mode else "Extraction"
    print(f"  {complete_label} complete: {len(succeeded)} succeeded, {len(failed)} failed")
    for d in failed:
        label_safe = labels[d].replace("/", "_").replace(".", "_")
        log_path = os.path.join(vscode_dir, f"extract_{label_safe}.log")
        print(f"    FAILED: {labels[d]}  (log: {log_path})")

    # ── Done ─────────────────────────────────────────────────────────────
    total_time = max(end_times.values()) - min(start_times.values()) if start_times else 0
    semgrep_flag = " --semgrep" if semgrep_mode else ""
    print(f"\n{'=' * 60}")
    print(f"  {complete_label} complete  ({int(total_time)}s)")
    print(f"  Logs: {vscode_dir}/extract_*.log")
    print()
    consolidate_cmd = (
        f'docker run --rm '
        f'-v "{root_dir}":/app/output '
        f'-v "{root_dir}":"{root_dir}" '
        f'alecmaly/sa-tool python3 /app/consolidate_outputs.py '
        f'-d "{root_dir}"{semgrep_flag}'
    )
    print(f"  Next steps:")
    print(f"    # Step 2: Consolidate")
    print(f"    {consolidate_cmd}")
    if not semgrep_mode:
        postprocess_cmd = (
            f'cd "{root_dir}" && docker run --rm '
            f'-v "$(pwd)":/app/output '
            f'-v "$(pwd)":"$(pwd)" '
            f'alecmaly/sa-tool /bin/bash /app/_process_static_analysis.sh'
        )
        print()
        print(f"    # Step 3: Postprocess")
        print(f"    {postprocess_cmd}")
    print(f"{'=' * 60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Detect sub-project roots for optimal LSP scanning"
    )
    parser.add_argument(
        "--project_dir", "-d", type=str, default=".",
        help="Directory to analyze (default: current directory)"
    )
    parser.add_argument(
        "--languages", "-l", type=str, default=None,
        help="Only check specific language(s), comma-separated"
    )
    parser.add_argument(
        "--docker", action="store_true", default=False,
        help="Emit Docker commands instead of local python commands"
    )
    parser.add_argument(
        "--json", dest="json_output", action="store_true", default=False,
        help="Output structured JSON (for LLM evaluation or programmatic use)"
    )
    parser.add_argument(
        "--json-file", dest="json_file", type=str, default=None,
        help="Write JSON output to file instead of stdout"
    )
    parser.add_argument(
        "--exclude", "-x", type=str, action="append", default=[],
        help=(
            "Exclude roots whose relative path matches any of these patterns. "
            "Supports glob syntax (fnmatch). Examples: "
            "'test*' 'vendor/*' 'packages/legacy-*' '**/fixtures'"
        )
    )
    parser.add_argument(
        "--run", action="store_true", default=False,
        help="Run the full pipeline (extract → consolidate → postprocess) with live progress"
    )
    parser.add_argument(
        "-P", "--parallel", type=int, default=3,
        help="Max parallel extraction jobs when using --run (default: 3)"
    )
    parser.add_argument(
        "--copy", action="store_true", default=False,
        help="Copy the xargs extract command to the clipboard (requires xclip or xsel on Linux)"
    )
    parser.add_argument(
        "--check-scanned", action="store_true", default=False,
        help=(
            "Show which directories already have non-empty scan data "
            "(function_calls.json / functions_html.json counts). "
            "When combined with -D or --run, skips already-scanned directories."
        )
    )
    parser.add_argument(
        "--split-depth", "-D", type=int, nargs="?", const=1, default=None, metavar="N",
        help=(
            "Split project by directory depth N for parallel scanning. "
            "Emits one scan command per subdirectory at depth N plus a root "
            "scan with --exclude-paths covering those subdirs. "
            "Skips marker detection for speed. "
            "Defaults to 1 when flag is given without a value."
        )
    )
    parser.add_argument(
        "--semgrep", action="store_true", default=False,
        help="Emit semgrep scan commands instead of LSP extraction commands"
    )
    parser.add_argument(
        "--no-partition-csharp", action="store_true", default=False,
        help=(
            "Disable C# solution partitioning. By default, large C# solutions "
            "are partitioned into groups with per-group .sln files for faster "
            "OmniSharp scanning. This flag reverts to the old behavior of one "
            "OmniSharp instance per project, all using the master .sln."
        )
    )
    parser.add_argument(
        "--csharp-groups", type=int, default=None,
        help="Number of C# partition groups (default: derived from --chunk-size)"
    )
    parser.add_argument(
        "--chunk-size", type=int, default=2000,
        help="Target number of files per chunk for C# partitioning (default: 2000)"
    )
    parser.add_argument(
        "--ilspy", action="store_true", default=False,
        help=(
            "ILSpy decompiled codebase mode. Creates .sln from .csproj files, "
            "fixes ProjectReferences, creates Directory.Build.props for net48, "
            "deduplicates assemblies with same AssemblyName (e.g. GAC variants), "
            "and partitions into group .sln files. Root .sln is NOT scanned — "
            "only group .sln files are scanned with separate output dirs."
        )
    )

    args = parser.parse_args()

    languages = None
    if args.languages:
        if args.languages.strip().lower() == "all":
            languages = None  # None = check all languages
        else:
            languages = [l.strip() for l in args.languages.split(",") if l.strip()]
            all_known = set(PROJECT_MARKERS.keys()) | set(LANGUAGE_EXTENSIONS.keys())
            unknown = [l for l in languages if l not in all_known]
            if unknown:
                print(
                    f"Warning: unknown language(s): {', '.join(unknown)}. "
                    f"Known languages: {', '.join(sorted(all_known))}",
                    file=sys.stderr,
                )

    root_dir = os.path.abspath(os.path.expanduser(args.project_dir))

    # --ilspy: set up decompiled C# project before detection
    if args.ilspy:
        print("=" * 60)
        print("  ILSpy Decompiled Project Setup")
        print("=" * 60)

        # Clean up stale group .sln files and scan_group dirs from previous runs
        _run_fix_csproj_for_lsp(root_dir)

        # Force C# language and partition mode
        if not languages:
            languages = ["c#"]
        elif "c#" not in languages:
            languages.append("c#")
        args.no_partition_csharp = False
        print()

    if args.split_depth is not None:
        print_split_commands(
            root_dir, args.split_depth,
            docker_mode=args.docker,
            parallelism=args.parallel,
            skip_scanned=args.check_scanned,
            do_copy=args.copy,
            run=args.run,
            semgrep_mode=args.semgrep,
        )
        return

    recommendations = detect_project_roots(root_dir, languages, exclude_patterns=args.exclude)

    if args.run:
        print_results(root_dir, recommendations, docker_mode=True, skip_scanned=args.check_scanned, do_copy=args.copy, semgrep_mode=args.semgrep, no_partition_csharp=args.no_partition_csharp, csharp_groups=args.csharp_groups, chunk_size=args.chunk_size)
        run_pipeline(root_dir, recommendations, parallelism=args.parallel,
                     skip_scanned=args.check_scanned, semgrep_mode=args.semgrep,
                     no_partition_csharp=args.no_partition_csharp,
                     csharp_groups=args.csharp_groups, chunk_size=args.chunk_size)
    elif args.json_output or args.json_file:
        emit_json(root_dir, recommendations, output_path=args.json_file)
    else:
        print_results(root_dir, recommendations, docker_mode=args.docker, skip_scanned=args.check_scanned, do_copy=args.copy, semgrep_mode=args.semgrep, no_partition_csharp=args.no_partition_csharp, csharp_groups=args.csharp_groups, chunk_size=args.chunk_size)


if __name__ == "__main__":
    main()
