# GP lock frame (papermode)
Blender addon - lock frame and view rotation to avoid unintentional time/move changes.

## [Download latest](https://github.com/Pullusb/GP_lock_frame/archive/master.zip)

Want to support me? [Check this page](http://www.samuelbernou.fr/donate)

---  

## Description

![lock frame](https://github.com/Pullusb/images_repo/raw/master/PAPERMOD_Lock_frame.png)

Lock you in space and/or time to focus on your 2D still painting \o/.  

Actually it's not specific to Grease pencil, but it was made with single static drawing in mind.

/!\ You do not want to save your user-prefs with the locks ON, always disable them before saving prefs (they affect the keymap).

## Why

Sometimes you accidentally move in time and new grease pencil stroke create a new unwanted frame.  
-> *Time lock* option fix the current frame and disable playback. `spacebar` also becomes another pan, like in 2D painting softwares.
Note: You souldn't use the timelock, if spacebar isn't used for `Play` in your keymapping.

Also in some session you can trigger accidentally the viewport rotation then have to remacth the view.  
-> *lock view* option switch to pan-only mode (the shortcut to rotate becomes also a pan)  



## Limitation

Because it use some hacks, it may not work well with multiple scenes (untested):
 - the lock view use a global keymap options (same behavior on all scene).
 - the lock time should work by scenes individually but the button may not be updated (untested).
 - as a result both button icons may not show the right state in multi-scene blend file.

---

## Changelog:

0.3.2 - 2020-12-12:

- fix: spacebar + click not working on GP draw mode
  - draw shortcut was overriding general 'window' keymap, added a specific 'Grease Pencil' keymap

0.3.1 - 2020-12-02:

- fix: preference repair operator not working

0.3.0 - 2020-12-02:

- 2.91 update:
  - fix incompatibility with 2.91 that has added other 'view3d.rotate' keymap items (not using MIDDLEMOUSE)
- fix: Bad behavior at keymap unregister
- feat: Better spacebar pan behavior (active when lock time is used)
  - now works exactly like 2D software (continuous spacebar + click)

0.2.3 - 2020-10-10:

- Added debug prints to explore bug in checks

0.2.2 - 2020-10-05:

- Added addon pref and a repair button to try a fix if user prefs has been saved with locks-on

0.2.1 - 2020-10-04:

- Add spacebar as another pan when time is locked (2D like)

0.1.2 - 2020-05-23:

- Fix: Apply saved locks at file opening or other blend loading (Locks were not applied even when showed as enabled at opening)

0.1.1 - 2020-05-15:

- version 1