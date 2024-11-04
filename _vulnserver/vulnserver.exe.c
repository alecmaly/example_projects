#include "vulnserver.exe.h"



void FUN_00401000(void)

{
                    // WARNING: Could not recover jumptable at 0x0040100c. Too many branches
                    // WARNING: Treating indirect jump as call
  atexit();
  return;
}



void ___mingw_CRTStartup(void)

{
  code *pcVar1;
  int *piVar2;
  undefined4 *puVar3;
  UINT uExitCode;
  _startupinfo local_14;
  char **local_10 [2];
  
  _SetUnhandledExceptionFilter_4((LPTOP_LEVEL_EXCEPTION_FILTER)0x401150);
  ___cpu_features_init();
  _fpreset();
  local_14.newmode = 0;
  ___getmainargs(&DAT_00405000,&__argv,local_10,DAT_00403000,&local_14);
  pcVar1 = _iob_exref;
  if (__CRT_fmode != 0) {
    __fmode = __CRT_fmode;
    __setmode(*(int *)(_iob_exref + 0x10),__CRT_fmode);
    __setmode(*(int *)(pcVar1 + 0x30),__CRT_fmode);
    __setmode(*(int *)(pcVar1 + 0x50),__CRT_fmode);
  }
  piVar2 = (int *)___p__fmode();
  *piVar2 = __fmode;
  __pei386_runtime_relocator();
  ___main();
  puVar3 = (undefined4 *)___p__environ();
  uExitCode = _main(DAT_00405000,__argv,(char **)*puVar3);
  __cexit();
                    // WARNING: Subroutine does not return
  _ExitProcess_4(uExitCode);
}



undefined4 _mainCRTStartup(void)

{
  bool bVar1;
  code *pcVar2;
  undefined4 *puStack_18;
  
  __set_app_type(1);
  ___mingw_CRTStartup();
  pcVar2 = *(code **)*puStack_18;
  if (pcVar2 < (code *)0xc0000092) {
    if (pcVar2 < (code *)0xc000008d) {
      if (pcVar2 == (code *)0xc0000005) {
        _signal(0xb);
        if (pcVar2 == (code *)0x1) {
          _signal(0xb);
          return 0xffffffff;
        }
        if (pcVar2 == (code *)0x0) {
          return 0;
        }
        (*pcVar2)(0xb);
        return 0xffffffff;
      }
      if (pcVar2 != (code *)0xc000001d) {
        return 0;
      }
LAB_004011c9:
      _signal(4);
      if (pcVar2 == (code *)0x1) {
        _signal(4);
        return 0xffffffff;
      }
      if (pcVar2 == (code *)0x0) {
        return 0;
      }
      (*pcVar2)(4);
      return 0xffffffff;
    }
  }
  else {
    if (pcVar2 == (code *)0xc0000094) {
      bVar1 = false;
      goto LAB_00401171;
    }
    if (pcVar2 == (code *)0xc0000096) goto LAB_004011c9;
    if (pcVar2 != (code *)0xc0000093) {
      return 0;
    }
  }
  bVar1 = true;
LAB_00401171:
  _signal(8);
  if (pcVar2 == (code *)0x1) {
    _signal(8);
    if (bVar1) {
      _fpreset();
    }
    return 0xffffffff;
  }
  if (pcVar2 == (code *)0x0) {
    return 0;
  }
  (*pcVar2)(8);
  return 0xffffffff;
}



int __cdecl _main(int _Argc,char **_Argv,char **_Env)

{
  u_short uVar1;
  int iVar2;
  size_t sVar3;
  char *pcVar4;
  size_t in_stack_fffffd60;
  int local_264;
  int local_260;
  undefined local_25c [28];
  int local_240;
  undefined4 local_23c;
  undefined4 local_238;
  undefined4 local_234;
  undefined4 local_230;
  int local_218;
  LPVOID local_214;
  SOCKET local_210;
  WSADATA local_20c;
  char local_7c [96];
  char local_1c [20];
  
  __alloca(in_stack_fffffd60);
  ___main();
  _memcpy(local_7c,
          "Usage: %s [port_number]\n\nIf no port number is provided, the default port of %s will be used.\n"
          ,0x5e);
  if (2 < _Argc) {
    _printf(local_7c,*_Argv,&DAT_0040405e);
    return 1;
  }
  if (_Argc == 2) {
    iVar2 = _atoi(_Argv[1]);
    if (((iVar2 < 1) || (iVar2 = _atoi(_Argv[1]), 0xffff < iVar2)) ||
       (sVar3 = _strlen(_Argv[1]), 6 < sVar3)) {
      _printf(local_7c,*_Argv,&DAT_0040405e);
      return 1;
    }
    _strncpy(local_1c,_Argv[1],6);
  }
  else {
    _strncpy(local_1c,"9999",6);
  }
  _printf("Starting vulnserver version %s\n",&DAT_00404063);
  _EssentialFunc1();
  _printf(
         "\nThis is vulnerable software!\nDo not allow access from untrusted systems or networks!\n\n"
         );
  local_210 = 0xffffffff;
  local_214 = (LPVOID)0xffffffff;
  local_218 = 0;
  local_260 = 0x10;
  local_240 = _WSAStartup_8(0x202,&local_20c);
  if (local_240 == 0) {
    _memset(&local_23c,0,0x20);
    local_238 = 2;
    local_234 = 1;
    local_230 = 6;
    local_23c = 1;
    local_240 = _getaddrinfo_16(0,local_1c,&local_23c,&local_218);
    if (local_240 == 0) {
      local_210 = _socket_12(*(int *)(local_218 + 4),*(int *)(local_218 + 8),
                             *(int *)(local_218 + 0xc));
      if (local_210 == 0xffffffff) {
        iVar2 = _WSAGetLastError_0();
        _printf("Socket failed with error: %ld\n",iVar2);
        _freeaddrinfo_4(local_218);
        _WSACleanup_0();
        local_264 = 1;
      }
      else {
        local_240 = _bind_12(local_210,*(sockaddr **)(local_218 + 0x18),*(int *)(local_218 + 0x10));
        if (local_240 == -1) {
          iVar2 = _WSAGetLastError_0();
          _printf("Bind failed with error: %d\n",iVar2);
          _closesocket_4(local_210);
          _WSACleanup_0();
          local_264 = 1;
        }
        else {
          _freeaddrinfo_4(local_218);
          local_240 = _listen_8(local_210,0x7fffffff);
          if (local_240 == -1) {
            iVar2 = _WSAGetLastError_0();
            _printf("Listen failed with error: %d\n",iVar2);
            _closesocket_4(local_210);
            _WSACleanup_0();
            local_264 = 1;
          }
          else {
            while (local_210 != 0) {
              _printf("Waiting for client connections...\n");
              local_214 = (LPVOID)_accept_12(local_210,(sockaddr *)local_25c,&local_260);
              if (local_214 == (LPVOID)0xffffffff) {
                iVar2 = _WSAGetLastError_0();
                _printf("Accept failed with error: %d\n",iVar2);
                _closesocket_4(local_210);
                _WSACleanup_0();
                return 1;
              }
              uVar1 = _htons_4(local_25c._2_2_);
              pcVar4 = _inet_ntoa_4((in_addr)local_25c._4_4_);
              _printf("Received a client connection from %s:%u\n",pcVar4,(uint)uVar1);
              _CreateThread_24((LPSECURITY_ATTRIBUTES)0x0,0,
                               (LPTHREAD_START_ROUTINE)&_ConnectionHandler_4,local_214,0,
                               (LPDWORD)0x0);
            }
            _closesocket_4(0);
            _WSACleanup_0();
            local_264 = 0;
          }
        }
      }
    }
    else {
      _printf("Getaddrinfo failed with error: %d\n",local_240);
      _WSACleanup_0();
      local_264 = 1;
    }
  }
  else {
    _printf("WSAStartup failed with error: %d\n",local_240);
    local_264 = 1;
  }
  return local_264;
}



void __cdecl _Function1(char *param_1)

{
  char local_9c [152];
  
  _strcpy(local_9c,param_1);
  return;
}



void __cdecl _Function2(char *param_1)

{
  char local_4c [72];
  
  _strcpy(local_4c,param_1);
  return;
}



void __cdecl _Function3(char *param_1)

{
  char local_7dc [2008];
  
  _strcpy(local_7dc,param_1);
  return;
}



void __cdecl _Function4(char *param_1)

{
  char local_3fc [1016];
  
  _strcpy(local_3fc,param_1);
  return;
}



int _recv_16(SOCKET s,char *buf,int len,int flags)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x0040252c. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = recv(s,buf,len,flags);
  return iVar1;
}



int _send_16(SOCKET s,char *buf,int len,int flags)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402534. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = send(s,buf,len,flags);
  return iVar1;
}



u_short _htons_4(u_short hostshort)

{
  u_short uVar1;
  
                    // WARNING: Could not recover jumptable at 0x0040253c. Too many branches
                    // WARNING: Treating indirect jump as call
  uVar1 = htons(hostshort);
  return uVar1;
}



char * _inet_ntoa_4(in_addr in)

{
  char *pcVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402544. Too many branches
                    // WARNING: Treating indirect jump as call
  pcVar1 = inet_ntoa(in);
  return pcVar1;
}



SOCKET _accept_12(SOCKET s,sockaddr *addr,int *addrlen)

{
  SOCKET SVar1;
  
                    // WARNING: Could not recover jumptable at 0x0040254c. Too many branches
                    // WARNING: Treating indirect jump as call
  SVar1 = accept(s,addr,addrlen);
  return SVar1;
}



int _listen_8(SOCKET s,int backlog)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402554. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = listen(s,backlog);
  return iVar1;
}



int _closesocket_4(SOCKET s)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x0040255c. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = closesocket(s);
  return iVar1;
}



int _bind_12(SOCKET s,sockaddr *addr,int namelen)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402564. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = bind(s,addr,namelen);
  return iVar1;
}



void _freeaddrinfo_4(void)

{
                    // WARNING: Could not recover jumptable at 0x0040256c. Too many branches
                    // WARNING: Treating indirect jump as call
  freeaddrinfo();
  return;
}



int _WSAGetLastError_0(void)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402574. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = WSAGetLastError();
  return iVar1;
}



SOCKET _socket_12(int af,int type,int protocol)

{
  SOCKET SVar1;
  
                    // WARNING: Could not recover jumptable at 0x0040257c. Too many branches
                    // WARNING: Treating indirect jump as call
  SVar1 = socket(af,type,protocol);
  return SVar1;
}



int _WSACleanup_0(void)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402584. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = WSACleanup();
  return iVar1;
}



void _getaddrinfo_16(void)

{
                    // WARNING: Could not recover jumptable at 0x0040258c. Too many branches
                    // WARNING: Treating indirect jump as call
  getaddrinfo();
  return;
}



int _WSAStartup_8(WORD wVersionRequired,LPWSADATA lpWSAData)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402594. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = WSAStartup(wVersionRequired,lpWSAData);
  return iVar1;
}



void _EssentialFunc1(void)

{
                    // WARNING: Could not recover jumptable at 0x0040259c. Too many branches
                    // WARNING: Treating indirect jump as call
  EssentialFunc1();
  return;
}



// WARNING: Removing unreachable block (ram,0x0040265b)
// WARNING: Removing unreachable block (ram,0x0040264d)
// WARNING: Removing unreachable block (ram,0x004025e1)
// WARNING: Removing unreachable block (ram,0x004025d2)
// WARNING: Globals starting with '_' overlap smaller symbols at the same address

undefined8 ___cpu_features_init(void)

{
  uint *puVar1;
  int iVar2;
  uint uVar3;
  byte in_CF;
  byte in_PF;
  byte in_AF;
  byte in_ZF;
  byte in_SF;
  byte in_TF;
  byte in_IF;
  byte in_OF;
  byte in_NT;
  byte in_AC;
  byte in_VIF;
  byte in_VIP;
  byte in_ID;
  uint uVar4;
  
  uVar4 = (uint)(in_NT & 1) * 0x4000 | (uint)(in_OF & 1) * 0x800 | (uint)(in_IF & 1) * 0x200 |
          (uint)(in_TF & 1) * 0x100 | (uint)(in_SF & 1) * 0x80 | (uint)(in_ZF & 1) * 0x40 |
          (uint)(in_AF & 1) * 0x10 | (uint)(in_PF & 1) * 4 | (uint)(in_CF & 1) |
          (uint)(in_ID & 1) * 0x200000 | (uint)(in_VIP & 1) * 0x100000 |
          (uint)(in_VIF & 1) * 0x80000 | (uint)(in_AC & 1) * 0x40000;
  uVar3 = uVar4 ^ 0x200000;
  uVar3 = ((uint)((uVar3 & 0x4000) != 0) * 0x4000 | (uint)((uVar3 & 0x800) != 0) * 0x800 |
           (uint)((uVar3 & 0x200) != 0) * 0x200 | (uint)((uVar3 & 0x100) != 0) * 0x100 |
           (uint)((uVar3 & 0x80) != 0) * 0x80 | (uint)((uVar3 & 0x40) != 0) * 0x40 |
           (uint)((uVar3 & 0x10) != 0) * 0x10 | (uint)((uVar3 & 4) != 0) * 4 |
           (uint)((uVar3 & 1) != 0) | (uint)((uVar3 & 0x200000) != 0) * 0x200000 |
          (uint)((uVar3 & 0x40000) != 0) * 0x40000) ^ uVar4;
  if ((uVar3 & 0x200000) != 0) {
    puVar1 = (uint *)cpuid_basic_info(0);
    uVar3 = *puVar1;
    uVar4 = puVar1[2];
    if (uVar3 != 0) {
      iVar2 = cpuid_Version_info(1);
      uVar3 = *(uint *)(iVar2 + 8);
      if ((uVar3 & 0x100) != 0) {
        ____cpu_features = ____cpu_features | 1;
      }
      if ((short)uVar3 < 0) {
        ____cpu_features = ____cpu_features | 2;
      }
      if ((uVar3 & 0x800000) != 0) {
        ____cpu_features = ____cpu_features | 4;
      }
      if ((uVar3 & 0x1000000) != 0) {
        ____cpu_features = ____cpu_features | 8;
      }
      if ((uVar3 & 0x2000000) != 0) {
        ____cpu_features = ____cpu_features | 0x10;
      }
      if ((uVar3 & 0x4000000) != 0) {
        ____cpu_features = ____cpu_features | 0x20;
      }
      if ((*(uint *)(iVar2 + 0xc) & 1) != 0) {
        ____cpu_features = ____cpu_features | 0x40;
      }
      if ((*(uint *)(iVar2 + 0xc) & 0x2000) != 0) {
        ____cpu_features = ____cpu_features | 0x80;
      }
      puVar1 = (uint *)cpuid(0x80000000);
      uVar3 = *puVar1;
      uVar4 = puVar1[2];
      if (0x80000000 < uVar3) {
        puVar1 = (uint *)cpuid(0x80000001);
        uVar3 = *puVar1;
        if ((int)puVar1[2] < 0) {
          ____cpu_features = ____cpu_features | 0x100;
        }
        uVar4 = puVar1[2] & 0x40000000;
        if (uVar4 != 0) {
          ____cpu_features = ____cpu_features | 0x200;
        }
      }
    }
  }
  return CONCAT44(uVar4,uVar3);
}



void ___report_error(char *param_1)

{
  FILE *_File;
  
  _File = (FILE *)(_iob_exref + 0x40);
  _fwrite("Mingw runtime failure:\n",1,0x17,_File);
  _vfprintf(_File,param_1,&stack0x00000008);
                    // WARNING: Subroutine does not return
  _abort();
}



void __fastcall ___write_memory(size_t param_1,void *param_2)

{
  LPCVOID in_EAX;
  SIZE_T SVar1;
  _MEMORY_BASIC_INFORMATION local_3c;
  DWORD local_20 [4];
  
  if (param_1 != 0) {
    SVar1 = _VirtualQuery_12(in_EAX,&local_3c,0x1c);
    if (SVar1 == 0) {
                    // WARNING: Subroutine does not return
      ___report_error("  VirtualQuery failed for %d bytes at address %p");
    }
    if ((local_3c.Protect != 4) && (local_3c.Protect != 0x40)) {
      _VirtualProtect_16(local_3c.BaseAddress,local_3c.RegionSize,0x40,local_20);
    }
    _memcpy(in_EAX,param_2,param_1);
    if ((local_3c.Protect != 4) && (local_3c.Protect != 0x40)) {
      _VirtualProtect_16(local_3c.BaseAddress,local_3c.RegionSize,local_20[0],local_20);
    }
  }
  return;
}



// WARNING: Removing unreachable block (ram,0x004027fe)
// WARNING: Removing unreachable block (ram,0x00402808)
// WARNING: Removing unreachable block (ram,0x00402812)
// WARNING: Removing unreachable block (ram,0x0040281c)
// WARNING: Removing unreachable block (ram,0x00402826)
// WARNING: Removing unreachable block (ram,0x00402830)
// WARNING: Removing unreachable block (ram,0x00402836)
// WARNING: Removing unreachable block (ram,0x00402892)
// WARNING: Removing unreachable block (ram,0x0040289e)
// WARNING: Removing unreachable block (ram,0x004028a6)
// WARNING: Removing unreachable block (ram,0x004028c9)
// WARNING: Removing unreachable block (ram,0x0040283d)
// WARNING: Removing unreachable block (ram,0x00402956)
// WARNING: Removing unreachable block (ram,0x00402849)
// WARNING: Removing unreachable block (ram,0x00402854)
// WARNING: Removing unreachable block (ram,0x00402859)
// WARNING: Removing unreachable block (ram,0x004028d0)
// WARNING: Removing unreachable block (ram,0x00402947)
// WARNING: Removing unreachable block (ram,0x004028d8)
// WARNING: Removing unreachable block (ram,0x004028e0)
// WARNING: Removing unreachable block (ram,0x0040286d)
// WARNING: Removing unreachable block (ram,0x00402910)
// WARNING: Removing unreachable block (ram,0x00402876)
// WARNING: Removing unreachable block (ram,0x0040287b)
// WARNING: Removing unreachable block (ram,0x004028f0)
// WARNING: Removing unreachable block (ram,0x00402938)
// WARNING: Removing unreachable block (ram,0x004028f7)
// WARNING: Removing unreachable block (ram,0x004028ff)
// WARNING: Removing unreachable block (ram,0x00402924)
// WARNING: Removing unreachable block (ram,0x00402933)

void __pei386_runtime_relocator(void)

{
  if (_was_init_31080 == 0) {
    _was_init_31080 = 1;
  }
  return;
}



void ___do_global_ctors(void)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  
  iVar1 = 0;
  do {
    iVar2 = iVar1;
    iVar1 = iVar2 + 1;
  } while ((&___CTOR_LIST__)[iVar2 + 1] != 0);
  if (iVar2 != 0) {
    puVar3 = &___CTOR_LIST__ + iVar2;
    do {
      (*(code *)*puVar3)();
      puVar3 = puVar3 + -1;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
  }
  FUN_00401000();
  return;
}



void ___main(void)

{
  if (_initialized != 0) {
    return;
  }
  _initialized = 1;
  ___do_global_ctors();
  return;
}



void __cdecl _fpreset(void)

{
  return;
}



// WARNING: Globals starting with '_' overlap smaller symbols at the same address

int * ___w32_sharedptr_get(void)

{
  ATOM in_AX;
  ATOM AVar1;
  UINT UVar2;
  uint uVar3;
  int *piVar4;
  uint uVar5;
  int iVar6;
  int iVar7;
  int *piVar8;
  CHAR aCStack_128 [32];
  char acStack_108 [48];
  CHAR aCStack_d8 [32];
  char acStack_b8 [60];
  undefined4 uStack_7c;
  CHAR local_5c [84];
  
  piVar8 = (int *)0x0;
  UVar2 = GetAtomNameA(in_AX,local_5c,0x42);
  iVar6 = 0x1f;
  uVar5 = 1;
  if (UVar2 != 0) {
    do {
      while (local_5c[iVar6] != 'A') {
        uVar5 = uVar5 * 2;
        iVar6 = iVar6 + -1;
        if (iVar6 < 0) goto LAB_00402a8b;
      }
      piVar8 = (int *)((uint)piVar8 | uVar5);
      uVar5 = uVar5 * 2;
      iVar6 = iVar6 + -1;
    } while (-1 < iVar6);
LAB_00402a8b:
    if (*piVar8 == 0x54) {
      return piVar8;
    }
    __assert();
  }
  piVar8 = (int *)__assert();
  uStack_7c = 0xf1;
  if (___w32_sharedptr != (int *)0x0) {
    return piVar8;
  }
  builtin_memcpy(aCStack_d8,"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",0x20);
  builtin_strncpy(acStack_b8,"-LIBGCCW32-EH-3-SJLJ-GTHR-MINGW32",0x22);
  AVar1 = FindAtomA(aCStack_d8);
  if (AVar1 == 0) {
    piVar8 = (int *)_malloc(0x54);
    if (piVar8 == (int *)0x0) {
                    // WARNING: Subroutine does not return
      _abort();
    }
    _memset(piVar8,0,0x54);
    piVar8[1] = (int)_abort;
    uVar5 = 1;
    piVar8[2] = (int)&___w32_sharedptr_default_unexpected;
    iVar6 = dw2_object_mutex_0;
    *piVar8 = 0x54;
    iVar7 = DAT_00405038;
    piVar8[10] = 0;
    piVar8[5] = iVar6;
    iVar6 = dw2_once_1;
    piVar8[6] = iVar7;
    iVar7 = DAT_00403010;
    piVar8[7] = iVar6;
    iVar6 = sjl_fc_key_2;
    piVar8[0xb] = -1;
    piVar8[8] = iVar7;
    piVar8[0xc] = iVar6;
    iVar6 = DAT_00403018;
    piVar8[0xd] = sjl_once_3;
    iVar7 = eh_globals_static_4;
    piVar8[0xe] = iVar6;
    iVar6 = DAT_00405058;
    piVar8[0xf] = iVar7;
    iVar7 = eh_globals_key_5;
    piVar8[0x11] = -1;
    piVar8[0x10] = iVar6;
    piVar8[0x12] = iVar7;
    iVar6 = eh_globals_once_6;
    piVar8[0x14] = DAT_00403020;
    iVar7 = 0x1f;
    piVar8[0x13] = iVar6;
    do {
      uVar3 = (uint)piVar8 & uVar5;
      uVar5 = uVar5 * 2;
      aCStack_128[iVar7] = (-(uVar3 == 0) & 0x20U) + 0x41;
      iVar7 = iVar7 + -1;
    } while (-1 < iVar7);
    builtin_strncpy(acStack_108,"-LIBGCCW32-EH-3-SJLJ-GTHR-MINGW32",0x22);
    AVar1 = AddAtomA(aCStack_128);
    if ((AVar1 == 0) || (piVar4 = ___w32_sharedptr_get(), piVar4 != piVar8)) {
      AVar1 = 0;
    }
    if (AVar1 != 0) goto LAB_00402d13;
    _free(piVar8);
    FindAtomA(aCStack_d8);
  }
  piVar8 = ___w32_sharedptr_get();
LAB_00402d13:
  ___w32_sharedptr = piVar8;
  ____w32_sharedptr_terminate = piVar8 + 1;
  ____w32_sharedptr_unexpected = piVar8 + 2;
  return piVar8 + 2;
}



void * __cdecl __alloca(size_t _Size)

{
  uint in_EAX;
  void *pvVar1;
  size_t *psVar2;
  code *UNRECOVERED_JUMPTABLE;
  
  psVar2 = &_Size;
  for (; 0xfff < in_EAX; in_EAX = in_EAX - 0x1000) {
    psVar2 = psVar2 + -0x400;
    *psVar2 = *psVar2;
  }
  *(undefined4 *)((int)psVar2 - in_EAX) = *(undefined4 *)((int)psVar2 - in_EAX);
                    // WARNING: Could not recover jumptable at 0x00402d7b. Too many branches
                    // WARNING: Treating indirect jump as call
  pvVar1 = (void *)(*UNRECOVERED_JUMPTABLE)();
  return pvVar1;
}



int __cdecl
___getmainargs(int *_Argc,char ***_Argv,char ***_Env,int _DoWildCard,_startupinfo *_StartInfo)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402d80. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = __getmainargs(_Argc,_Argv,_Env,_DoWildCard,_StartInfo);
  return iVar1;
}



void ___p__fmode(void)

{
                    // WARNING: Could not recover jumptable at 0x00402d88. Too many branches
                    // WARNING: Treating indirect jump as call
  __p__fmode();
  return;
}



void ___p__environ(void)

{
                    // WARNING: Could not recover jumptable at 0x00402d90. Too many branches
                    // WARNING: Treating indirect jump as call
  __p__environ();
  return;
}



void __cdecl __cexit(void)

{
                    // WARNING: Could not recover jumptable at 0x00402d98. Too many branches
                    // WARNING: Treating indirect jump as call
  _cexit();
  return;
}



int __cdecl __setmode(int _FileHandle,int _Mode)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402da0. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = _setmode(_FileHandle,_Mode);
  return iVar1;
}



// WARNING: Unknown calling convention -- yet parameter storage is locked

void _signal(int param_1)

{
                    // WARNING: Could not recover jumptable at 0x00402da8. Too many branches
                    // WARNING: Treating indirect jump as call
  signal(param_1);
  return;
}



ulong __cdecl _strtoul(char *_Str,char **_EndPtr,int _Radix)

{
  ulong uVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402db0. Too many branches
                    // WARNING: Treating indirect jump as call
  uVar1 = strtoul(_Str,_EndPtr,_Radix);
  return uVar1;
}



int __cdecl _strncmp(char *_Str1,char *_Str2,size_t _MaxCount)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402db8. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = strncmp(_Str1,_Str2,_MaxCount);
  return iVar1;
}



void * __cdecl _malloc(size_t _Size)

{
  void *pvVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402dc0. Too many branches
                    // WARNING: Treating indirect jump as call
  pvVar1 = malloc(_Size);
  return pvVar1;
}



char * __cdecl _strcpy(char *_Dest,char *_Source)

{
  char *pcVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402dc8. Too many branches
                    // WARNING: Treating indirect jump as call
  pcVar1 = strcpy(_Dest,_Source);
  return pcVar1;
}



void * __cdecl _memcpy(void *_Dst,void *_Src,size_t _Size)

{
  void *pvVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402dd0. Too many branches
                    // WARNING: Treating indirect jump as call
  pvVar1 = memcpy(_Dst,_Src,_Size);
  return pvVar1;
}



void * __cdecl _memset(void *_Dst,int _Val,size_t _Size)

{
  void *pvVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402dd8. Too many branches
                    // WARNING: Treating indirect jump as call
  pvVar1 = memset(_Dst,_Val,_Size);
  return pvVar1;
}



char * __cdecl _strncpy(char *_Dest,char *_Source,size_t _Count)

{
  char *pcVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402de0. Too many branches
                    // WARNING: Treating indirect jump as call
  pcVar1 = strncpy(_Dest,_Source,_Count);
  return pcVar1;
}



size_t __cdecl _strlen(char *_Str)

{
  size_t sVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402de8. Too many branches
                    // WARNING: Treating indirect jump as call
  sVar1 = strlen(_Str);
  return sVar1;
}



int __cdecl _atoi(char *_Str)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402df0. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = atoi(_Str);
  return iVar1;
}



int __cdecl _printf(char *_Format,...)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402df8. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = printf(_Format);
  return iVar1;
}



size_t __cdecl _fwrite(void *_Str,size_t _Size,size_t _Count,FILE *_File)

{
  size_t sVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402e00. Too many branches
                    // WARNING: Treating indirect jump as call
  sVar1 = fwrite(_Str,_Size,_Count,_File);
  return sVar1;
}



int __cdecl _vfprintf(FILE *_File,char *_Format,va_list _ArgList)

{
  int iVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402e08. Too many branches
                    // WARNING: Treating indirect jump as call
  iVar1 = vfprintf(_File,_Format,_ArgList);
  return iVar1;
}



void __cdecl _abort(void)

{
                    // WARNING: Could not recover jumptable at 0x00402e10. Too many branches
                    // WARNING: Subroutine does not return
                    // WARNING: Treating indirect jump as call
  abort();
  return;
}



void __assert(void)

{
                    // WARNING: Could not recover jumptable at 0x00402e18. Too many branches
                    // WARNING: Treating indirect jump as call
  _assert();
  return;
}



void __cdecl _free(void *_Memory)

{
                    // WARNING: Could not recover jumptable at 0x00402e20. Too many branches
                    // WARNING: Treating indirect jump as call
  free(_Memory);
  return;
}



LPTOP_LEVEL_EXCEPTION_FILTER
_SetUnhandledExceptionFilter_4(LPTOP_LEVEL_EXCEPTION_FILTER lpTopLevelExceptionFilter)

{
  LPTOP_LEVEL_EXCEPTION_FILTER pPVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402e28. Too many branches
                    // WARNING: Treating indirect jump as call
  pPVar1 = SetUnhandledExceptionFilter(lpTopLevelExceptionFilter);
  return pPVar1;
}



void _ExitProcess_4(UINT uExitCode)

{
                    // WARNING: Could not recover jumptable at 0x00402e30. Too many branches
                    // WARNING: Subroutine does not return
                    // WARNING: Treating indirect jump as call
  ExitProcess(uExitCode);
  return;
}



HANDLE _CreateThread_24(LPSECURITY_ATTRIBUTES lpThreadAttributes,SIZE_T dwStackSize,
                       LPTHREAD_START_ROUTINE lpStartAddress,LPVOID lpParameter,
                       DWORD dwCreationFlags,LPDWORD lpThreadId)

{
  HANDLE pvVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402e38. Too many branches
                    // WARNING: Treating indirect jump as call
  pvVar1 = CreateThread(lpThreadAttributes,dwStackSize,lpStartAddress,lpParameter,dwCreationFlags,
                        lpThreadId);
  return pvVar1;
}



SIZE_T _VirtualQuery_12(LPCVOID lpAddress,PMEMORY_BASIC_INFORMATION lpBuffer,SIZE_T dwLength)

{
  SIZE_T SVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402e40. Too many branches
                    // WARNING: Treating indirect jump as call
  SVar1 = VirtualQuery(lpAddress,lpBuffer,dwLength);
  return SVar1;
}



BOOL _VirtualProtect_16(LPVOID lpAddress,SIZE_T dwSize,DWORD flNewProtect,PDWORD lpflOldProtect)

{
  BOOL BVar1;
  
                    // WARNING: Could not recover jumptable at 0x00402e48. Too many branches
                    // WARNING: Treating indirect jump as call
  BVar1 = VirtualProtect(lpAddress,dwSize,flNewProtect,lpflOldProtect);
  return BVar1;
}


