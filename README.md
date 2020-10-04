# GP lock frame (papermode)
Blender addon - lock frame and view rotation to avoid unintentional time/move changes.

## [Download latest](https://github.com/Pullusb/GP_lock_frame/archive/master.zip)

Want to support me? [Check this page](http://www.samuelbernou.fr/donate)

---  

## Description

![lock frame](https://github.com/Pullusb/images_repo/raw/master/PAPERMOD_Lock_frame.png)

Lock you in space and/or time to focus on your 2D still painting \o/.  

Actually it's not specific to Grease pencil, but it was made with single static drawing in mind.

## Why

Sometimes you accidentally move in time and new grease pencil stroke create a new unwanted frame.  
-> *Time lock* option fix the current frame and disable playback (since 0.2.1 spacebar becomes another pan, like 2D painting software)  
Note: Untested if spacebar is'nt used for `Play`.

Also in some session you can trigger accidentally the viewport rotation then have to remacth the view.  
-> *lock view* option switch to pan-only mode (the shortcut to rotate becomes also a pan)

## Limitation

Because it use some hacks, it may not work well with multiple scenes (untested):
 - the lock view use a global keymap options (same behavior on all scene).
 - the lock time should work by scenes individually but the button may not be updated (untested).
 - as a result both button icons may not show the right state in multi-scene blend file.

---

## Changelog:

  2020-10-04 - 0.2.1:

  - Add spacebar as another pan when time is locked (2D like)

  2020-05-23 - 0.1.2:

  - Fix: Apply saved locks at file opening or other blend loading (Locks were not applied even when showed as enabled at opening)

  2020-05-15 - 0.1.1:

  - version 1