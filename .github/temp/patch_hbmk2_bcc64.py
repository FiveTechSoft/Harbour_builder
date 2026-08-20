"""Patch hbmk2.prg AND config/win/bcc.mk for BCC 7.7 (Clang-based) bcc64 support."""
import sys, os

# --- Patch hbmk2.prg ---
f = sys.argv[1] if len(sys.argv) > 1 else os.path.join("utils", "hbmk2", "hbmk2.prg")
c = open(f, "r", encoding="utf-8").read()

patches = [
    # 1. bcc64 auto-detection
    (
        '{ {|| _BCC_BIN_DETECT()        }, "bcc"    }, ; /* TODO: Add bcc64 auto-detection */',
        '{ {|| iif( FindInPath( "bcc32.exe" ) != NIL, FindInPath( "bcc32.exe" ), FindInPath( "bcc64.exe" ) ) }, iif( FindInPath( "bcc32.exe" ) != NIL, "bcc", "bcc64" ) }, ;',
    ),
    # 2. Extend BCC setup to include bcc64
    (
        'IF hbmk[ _HBMK_cCOMP ] == "bcc" /* TODO: Add support for bcc64 */',
        'IF hbmk[ _HBMK_cCOMP ] == "bcc" .OR. hbmk[ _HBMK_cCOMP ] == "bcc64"',
    ),
    # 3. Fix cfg file detection for bcc64
    (
        '            ! hb_FileExists( hb_FNameDir( cPath_CompC ) + ".." + hb_ps() + "Bin" + hb_ps() + "bcc32.cfg" ) .OR. ;\n            ! hb_FileExists( hb_FNameDir( cPath_CompC ) + ".." + hb_ps() + "Bin" + hb_ps() + "ilink32.cfg" )',
        '            ! hb_FileExists( hb_FNameDir( cPath_CompC ) + ".." + hb_ps() + "Bin" + hb_ps() + iif( hbmk[ _HBMK_cCOMP ] == "bcc64", "bcc64.cfg", "bcc32.cfg" ) ) .OR. ;\n            ! hb_FileExists( hb_FNameDir( cPath_CompC ) + ".." + hb_ps() + "Bin" + hb_ps() + iif( hbmk[ _HBMK_cCOMP ] == "bcc64", "ilink64.cfg", "ilink32.cfg" ) )',
    ),
    # 4. Add dinkumware64 include path
    (
        '            tmp := hb_PathNormalize( hb_FNameDir( cPath_CompC ) + ".." + hb_ps() + "Include" + hb_ps() + "dinkumware" )\n            IF hb_DirExists( tmp )\n               AAdd( hbmk[ _HBMK_aINCPATH ], tmp )\n            ENDIF',
        '            FOR EACH tmp IN { "dinkumware", "dinkumware64" }\n               tmp := hb_PathNormalize( hb_FNameDir( cPath_CompC ) + ".." + hb_ps() + "Include" + hb_ps() + tmp )\n               IF hb_DirExists( tmp )\n                  AAdd( hbmk[ _HBMK_aINCPATH ], tmp )\n               ENDIF\n            NEXT',
    ),
    # 5. Skip -tW for bcc64
    (
        '         IF hbmk[ _HBMK_lGUI ]\n            AAdd( hbmk[ _HBMK_aOPTC ], "-tW" )\n         ENDIF',
        '         IF hbmk[ _HBMK_lGUI ] .AND. hbmk[ _HBMK_cCOMP ] != "bcc64"\n            AAdd( hbmk[ _HBMK_aOPTC ], "-tW" )\n         ENDIF',
    ),
    # 6. Remove -q flag for bcc64
    (
        'cOpt_CompC := "-c -q" + iif( hbmk[ _HBMK_cCOMP ] == "bcc64", "", " -CP437" )',
        'cOpt_CompC := "-c" + iif( hbmk[ _HBMK_cCOMP ] == "bcc64", "", " -q" ) + iif( hbmk[ _HBMK_cCOMP ] == "bcc64", "", " -CP437" )',
    ),
    # 7. Skip BCC32 optimization flags for bcc64
    (
        'cOpt_CompC += " -d -O2" + iif( hbmk[ _HBMK_cCOMP ] == "bcc64", "", " -OS -Ov -Oc -Oi -6" )',
        'IF hbmk[ _HBMK_cCOMP ] == "bcc64"\n               cOpt_CompC += " -O2"\n            ELSE\n               cOpt_CompC += " -d -O2 -OS -Ov -Oc -Oi -6"\n            ENDIF',
    ),
    # 8. Skip -tWM for bcc64 (non-xHarbour path)
    (
        '         ELSE\n            AAdd( hbmk[ _HBMK_aOPTC ], "-tWM" )\n         ENDIF\n         IF hbmk[ _HBMK_cCOMP ] == "bcc64"',
        '         ELSE\n            IF hbmk[ _HBMK_cCOMP ] != "bcc64"\n               AAdd( hbmk[ _HBMK_aOPTC ], "-tWM" )\n            ENDIF\n         ENDIF\n         IF hbmk[ _HBMK_cCOMP ] == "bcc64"',
    ),
    # 9. Fix warning flags for bcc64
    (
        '            CASE _WARN_YES ; AAdd( hbmk[ _HBMK_aOPTC ], "-w -Q" ) ; EXIT\n            CASE _WARN_NO  ; AAdd( hbmk[ _HBMK_aOPTC ], "-w-" )   ; EXIT',
        '            CASE _WARN_YES ; AAdd( hbmk[ _HBMK_aOPTC ], "-w" ) ; EXIT\n            CASE _WARN_NO  ; AAdd( hbmk[ _HBMK_aOPTC ], "-w" )   ; EXIT',
    ),
    # 10. Fix output directory flag for bcc64
    (
        '                  AAdd( hbmk[ _HBMK_aOPTC ], "-n{OD}" )',
        '                  IF hbmk[ _HBMK_cCOMP ] == "bcc64"\n                     AAdd( hbmk[ _HBMK_aOPTC ], "-o{OD}" )\n                  ELSE\n                     AAdd( hbmk[ _HBMK_aOPTC ], "-n{OD}" )\n                  ENDIF',
    ),
]

count = 0
for i, (old, new) in enumerate(patches):
    if old in c:
        c = c.replace(old, new, 1)
        count += 1
        print(f"hbmk2 OK {i+1}")
    else:
        print(f"hbmk2 SKIP {i+1}")

open(f, "w", encoding="utf-8").write(c)
print(f"hbmk2: {count}/{len(patches)} patches applied")

# --- Patch config/win/bcc.mk ---
f2 = os.path.join("config", "win", "bcc.mk")
c2 = open(f2, "r", encoding="utf-8").read()

bccmk_patches = [
    # Fix CFLAGS line 25: skip -q -tWM -CP437 for bcc64
    (
        'CFLAGS += -q -tWM -CP437',
        'ifneq ($(HB_COMPILER),bcc64)\nCFLAGS += -q -tWM -CP437\nendif',
    ),
    # Fix warning flags line 27-31: skip BCC32 warning flags for bcc64
    (
        'ifeq ($(HB_BUILD_WARN),no)\n   CFLAGS += -w-aus -w-ccc -w-csu -w-ovf -w-par -w-rch -w-spa\nelse\n   CFLAGS += -w -Q -w-sig\nendif',
        'ifeq ($(HB_COMPILER),bcc64)\n   ifeq ($(HB_BUILD_WARN),no)\n      CFLAGS += -w\n   else\n      CFLAGS += -w\n   endif\nelse\n   ifeq ($(HB_BUILD_WARN),no)\n      CFLAGS += -w-aus -w-ccc -w-csu -w-ovf -w-par -w-rch -w-spa\n   else\n      CFLAGS += -w -Q -w-sig\n   endif\nendif',
    ),
    # Fix optimization flags: skip -d -OS -Ov -Oc for bcc64
    (
        '   ifeq ($(HB_COMPILER),bcc64)\n      CFLAGS += -d -O2 -OS -Ov -Oc\n   else',
        '   ifeq ($(HB_COMPILER),bcc64)\n      CFLAGS += -O2\n   else',
    ),
    # Fix dynlib rule to use c0d64.o for bcc64
    (
        '   $(DY) $(DFLAGS) $(HB_USER_DFLAGS) c0d32.obj @__dyn__.tmp',
        'ifeq ($(HB_COMPILER),bcc64)\n   $(DY) $(DFLAGS) $(HB_USER_DFLAGS) c0d64.o @__dyn__.tmp\nelse\n   $(DY) $(DFLAGS) $(HB_USER_DFLAGS) c0d32.obj @__dyn__.tmp\nendif',
    ),
]

count2 = 0
for i, (old, new) in enumerate(bccmk_patches):
    if old in c2:
        c2 = c2.replace(old, new, 1)
        count2 += 1
        print(f"bcc.mk OK {i+1}")
    else:
        print(f"bcc.mk SKIP {i+1}")

open(f2, "w", encoding="utf-8").write(c2)
print(f"bcc.mk: {count2}/{len(bccmk_patches)} patches applied")
