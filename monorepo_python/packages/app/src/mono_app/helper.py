from mono_shared.util import hello     # absolute import across workspace pkgs


def run() -> None:
    print(hello("from helper"))
