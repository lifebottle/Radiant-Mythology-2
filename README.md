# Radiant-Mythology-2
Attempt to complete English patch for Tales of the World: Radiant Mythology 2

# Unpacking Files
1. Use QuickBMS script `rm2_arc.bms` to unpack the `ARC` files.
2. Unpacking may have some errors with duplicate files, use the `s` option to skip them all for now.
3. Sample command: `quickbms.exe -d rm2_arc.bms D:\rm2\totw-rm2_original`
4. See `totw-rm2_extracted.txt` for list of files extracted.


# Repacking Files
1. Use QuickBMS script `rm2_arc.bms` to pack the `ARC` files.  Backup oroginal files!
2. Sample command: `quickbms.exe -r -w rm2_arc.bms D:\rm2\totw-rm2_original PSP_GAME`


# Hints
1. From the existing patch, it looks like the `PSPGAME\SYSDIR\EBOOT.BIN` is where most of the menu text is.
1. `PSP_GAME\USRDIR\quest\qdata.bin` was also translated
1. The 'SCR` files are proabaly story/skit text


# Resources
[QuickBMS script to unpack ARC files (PSP)](https://m.blog.naver.com/physics1114/220350378050)
