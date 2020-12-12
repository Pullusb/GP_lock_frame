'''
Copyright (C) 2020 Samuel Bernou
bernou.samuel@gmail.com

Created by Samuel Bernou

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "GP lock frame",
    "description": "Paper mode: Lock viewport rotation + lock current frame = Easier 2D still painting",
    "author": "Samuel Bernou",
    "version": (0, 3, 2),
    "blender": (2, 83, 0),
    "location": "View3D > topbar right corner",
    "warning": "",
    "doc_url": "https://github.com/Pullusb/GP_lock_frame",
    "category": "Object" }


import bpy
from bpy.app.handlers import persistent
import os


def get_addon_prefs():
    addon_name = os.path.splitext(__name__)[0]
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons[addon_name].preferences
    return addon_prefs

class PAPERMOD_lock_time(bpy.types.Operator):
    bl_idname = "papermod.lock_time"
    bl_label = "lock time"
    bl_description = "Lock time at the moment of activation, disable playback"
    bl_options = {"REGISTER"}#, "INTERNAL"

    def execute(self, context):
        lock_time_toggle(context)
        return {"FINISHED"}

def lock_time_toggle(context):
    '''get a context and lock scene frame with a handler and update change'''
    # adding current frame as lock
    context.scene.lockprop.holdframe = context.scene.frame_current
    # if already locked remove handle, else create it
    if not lock_time_handle.__name__ in [hand.__name__ for hand in bpy.app.handlers.frame_change_pre]:
        bpy.app.handlers.frame_change_pre.append(lock_time_handle)
        context.scene.lockprop.time = True
        lock_time()
    else:
        bpy.app.handlers.frame_change_pre.remove(lock_time_handle)
        context.scene.lockprop.time = False
        unlock_time()

def lock_time_handle(scene):
    # https://docs.blender.org/api/current/bpy.app.handlers.html
    scene.frame_current = scene.lockprop.holdframe

    #cancel anim
    if bpy.context.screen.is_animation_playing:
        bpy.ops.screen.animation_cancel()
        ## triggered whenever time cursor move (not only at playback)
        # bpy.ops.wm.call_menu(name="PAPERMOD_MT_warning")

"""
## optional warning menu for pop up (but no good method to detect if playback is triggered only)
# class PAPERMOD_MT_warning(bpy.types.Menu):
#     '''If playback attempt launch a helper'''
#     # bl_idname = "PAPERMOD_MT_warning"
#     bl_label = "Playback disabled by lock time option"
#     def draw(self, context):
#         layout = self.layout
#         ## layout.label(text='Playback is disabled by the lock time, Unlock to keep playback')
#         layout.operator(PAPERMOD_lock_time.bl_idname, text = "lock time", icon = 'MOD_TIME', depress = context.scene.lockprop.time)
#         layout.operator(PAPERMOD_lock_view.bl_idname, text = "lock view", icon = 'LOCKVIEW_ON', depress = context.scene.lockprop.view)

## optional Panel
# class PAPERMOD_toolpanel(bpy.types.Panel):
#     # bl_idname = "Papermod"
#     bl_label = "Papermod"
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_category = "Gpencil"

#     def draw(self, context):
#         layout = self.layout
#         layout.label(text='lock tools:')
#         layout.operator(PAPERMOD_lock_time.bl_idname, text = "", icon = 'MOD_TIME', depress = context.scene.lockprop.time)
#         layout.operator(PAPERMOD_lock_view.bl_idname, text = "", icon = 'LOCKVIEW_ON', depress = context.scene.lockprop.view)
"""

def get_mouse_rotate_kmi():
    for kmi in bpy.context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items:
        if kmi.idname == 'view3d.rotate':
            if kmi.type == 'MIDDLEMOUSE':
                return kmi
    if get_addon_prefs().debug:
        print("Can't find 'view3d.rotate' with MIDDLEMOUSE type in wm.keyconfigs.user.keymaps['3D View']")

class PAPERMOD_lock_view(bpy.types.Operator):
    bl_idname = "papermod.lock_view"
    bl_label = "lock view"
    bl_description = "Lock view rotation, rotate shortcut temporarily binded to pan"
    bl_options = {"REGISTER"}#, "INTERNAL"

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        ## multiple 
        # if context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items['view3d.rotate'].active:
        if get_mouse_rotate_kmi().active:
            lock_orbit()
            context.scene.lockprop.view = True
        else:
            unlock_orbit()
            context.scene.lockprop.view = False

        return {"FINISHED"}

        
def papermod_lock_buttons_UI(self, context):
    """papermod header buttons"""
    layout = self.layout
    row = layout.row(align=True)
    # row.label(text='Lock')
    row.operator(PAPERMOD_lock_time.bl_idname,
    text = "", icon = 'MOD_TIME', depress = context.scene.lockprop.time)

    row.operator(PAPERMOD_lock_view.bl_idname,
    text = "", icon = 'LOCKVIEW_ON', depress = context.scene.lockprop.view)



### --- Time spacebar keymaps stuff

def lock_time():
    # deactivate default rotate keymap
    bpy.context.window_manager.keyconfigs.user.keymaps['Frames'].keymap_items['screen.animation_play'].active = False
    # bind (or activate if already binded) addon secondary keymap to use rotate cmd as pan
    bind_time_keymap()

def unlock_time():
    prefs = get_addon_prefs()#Dbg

    user_play_km = bpy.context.window_manager.keyconfigs.user.keymaps.get('Frames')
    if not user_play_km:
        print("in unlock_orbit: user > Frames not found")
        return# pass# return to avoid checking addon keymap ?
    else:
        play = bpy.context.window_manager.keyconfigs.user.keymaps['Frames'].keymap_items.get('screen.animation_play')
        if play:
            if prefs.debug: print('in unlock_time: user > Frames > screen.animation_play exists - (re)activate it')#Dbg
            play.active = True
        else:
            print("not found: bpy.context.window_manager.keyconfigs.user.keymaps['Frames'].keymap_items.get('screen.animation_play')")

    # disable (pass if keymap was not registered yet)
    if bpy.context.window_manager.keyconfigs.addon.keymaps.get('Window'):
        spacebar_move = bpy.context.window_manager.keyconfigs.addon.keymaps['Window'].keymap_items.get('view3d.move')
        if spacebar_move:
            if prefs.debug: print('in unlock_time: addon > Window > view3d.move exists - Disable it')#Dbg
            spacebar_move.active = False
        else:
            print("not found: bpy.context.window_manager.keyconfigs.addon.keymaps['Window'].keymap_items.get('view3d.move')")
            pass

    if bpy.context.window_manager.keyconfigs.addon.keymaps.get('Grease Pencil'):
        spacebar_move = bpy.context.window_manager.keyconfigs.addon.keymaps['Grease Pencil'].keymap_items.get('view3d.move')
        if spacebar_move:
            if prefs.debug: print('in unlock_time: addon > Grease Pencil > view3d.move exists - Disable it')#Dbg
            spacebar_move.active = False
        else:
            print("not found: bpy.context.window_manager.keyconfigs.addon.keymaps['Grease Pencil'].keymap_items.get('view3d.move')")
            pass


### === keymaps

addon_time_keymaps = []

def bind_time_keymap(): 
    ## add spacebar as third pan shortcut when time is locked (top for laptop) !
    ## Check if hotkey has already been set, to avoid duplicates when auto creating hotkey
    # km = bpy.context.window_manager.keyconfigs.addon.keymaps.get("3D View")
    
    prefs = get_addon_prefs()#Dbg
    
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.get("Window")# Screen
    if not km:
        km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
            "Window", space_type='EMPTY', region_type='WINDOW')# Window

    thekeymap = km.keymap_items.get("view3d.move")
    if not thekeymap:#"view3d.move" not in km.keymap_items:
        if prefs.debug: print('in bind_time_keymap: addon > Window > view3d.move not exists - create it')#Dbg
        ## OPT: Can check if spacebar is used by the user for this (skip if it's use gor somthing else...)
        # kplay = bpy.context.window_manager.keyconfigs.user.keymaps['Frames'].keymap_items['screen.animation_play']
        
        ## hardcoded :
        ## Space immediately drag
        # kmi = km.keymap_items.new(idname='view3d.move', type='SPACE', value='PRESS')
        ## 2D like (space + continuous click to drag)
        kmi = km.keymap_items.new(idname='view3d.move', type='LEFTMOUSE', value='PRESS', key_modifier='SPACE')
        addon_time_keymaps.append((km, kmi))
    else:
        if prefs.debug: print('in bind_time_keymap: addon > Window > view3d.move exists - activate it')#Dbg
        thekeymap.active = True

    ## add keymap in Gpencil else doesn't work in draw mode.
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.get("Grease pencil")# Screen
    if not km:
        print('Creating addon "Grease pencil" keymap cat')
        km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
            "Grease Pencil", space_type='EMPTY', region_type='WINDOW')
    thekeymap = km.keymap_items.get("view3d.move")
    
    if not thekeymap:#"view3d.move" not in km.keymap_items:
        if prefs.debug: print('in bind_time_keymap: addon > Grease Pencil > view3d.move not exists - create it')#Dbg
        kmi = km.keymap_items.new(idname='view3d.move', type='LEFTMOUSE', value='PRESS', key_modifier='SPACE')
        addon_time_keymaps.append((km, kmi))
    else:
        if prefs.debug: print('in bind_time_keymap: addon > Grease Pencil > view3d.move exists - activate it')#Dbg
        thekeymap.active = True

def unbind_time_keymap():
    if not bpy.context.window_manager.keyconfigs.addon.keymaps.get("Window"):
        return
    if not bpy.context.window_manager.keyconfigs.addon.keymaps['Window'].keymap_items.get('view3d.move'):
        return

    for km, kmi in addon_time_keymaps:
        km.keymap_items.remove(kmi)
    addon_time_keymaps.clear()

### --- Orbit keymaps stuff


def lock_orbit():
    # deactivate default rotate keymap
    rot_kmi = get_mouse_rotate_kmi()
    rot_kmi.active = False
    # bind (or activate if already binded) addon secondary keymap to use rotate cmd as pan
    bind_keymap()

def unlock_orbit():
    prefs = get_addon_prefs()#Dbg

    user_view_km = bpy.context.window_manager.keyconfigs.user.keymaps.get('3D View')
    if not user_view_km:
        print("in unlock_orbit: user > 3D View not found")
        return# pass# return to avoid checking addon keymap ?
    else:
        ## since 2.91 there are more than on 'view3d.rotate' idname active
        # rot = bpy.context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items.get('view3d.rotate')

        rot = get_mouse_rotate_kmi()
        if rot:
            if prefs.debug: print('in unlock_orbit: user > 3D View > view3d.move exists - (re)activate it')#Dbg
            rot.active = True
        else:
            print("not found: user.keymaps['3D View'] 'view3d.rotate' with MIDDLEMOUSE type")

    # disable (pass if keymap was not registered yet)
    if not bpy.context.window_manager.keyconfigs.addon.keymaps.get('Screen'):
        if prefs.debug: print("in unlock_orbit: not found bpy.context.window_manager.keyconfigs.addon.keymaps['Screen']")#Dbg
        return

    pan = bpy.context.window_manager.keyconfigs.addon.keymaps['Screen'].keymap_items.get('view3d.move')
    if pan:
        if prefs.debug: print('in unlock_orbit: addon > Screen > view3d.move exists - disable it')#Dbg
        pan.active = False
    else:
        if prefs.debug: print("in unlock_orbit: not found: bpy.context.window_manager.keyconfigs.addon.keymaps['Screen'].keymap_items.get('view3d.move')")#Dbg
        pass


addon_keymaps = []

def bind_keymap():
    prefs = get_addon_prefs()#Dbg
    ## Check if hotkey has already been set, to avoid duplicates when auto creating hotkey
    # km = bpy.context.window_manager.keyconfigs.addon.keymaps.get("3D View")
    km = bpy.context.window_manager.keyconfigs.addon.keymaps.get("Screen")
    if not km:
        km = bpy.context.window_manager.keyconfigs.addon.keymaps.new(
            "Screen", space_type='EMPTY', region_type='WINDOW')# doesn't work in "3D View", space_type='VIEW_3D'

    # create another pan shortcut at addon level and copy default rotate settings so they both do pan

    thekeymap = km.keymap_items.get("view3d.move")
    if not thekeymap:#"view3d.move" not in km.keymap_items:
        if prefs.debug: print('in bind_keymap: screen->view3d.move not exists, create entry')#Dbg

        # krot = bpy.context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items['view3d.rotate']
        krot = get_mouse_rotate_kmi()
        kmov = bpy.context.window_manager.keyconfigs.user.keymaps['3D View'].keymap_items['view3d.move']
        # print(kmov.idname, krot.type, krot.value, krot.any, krot.alt,krot.ctrl, krot.shift)
        kmi = km.keymap_items.new(idname=kmov.idname, type=krot.type , value=krot.value, any=krot.any, alt=krot.alt, ctrl=krot.ctrl, shift=krot.shift)
        ## hardcoded : kmi = km.keymap_items.new(idname='view3d.move', type='MIDDLEMOUSE' , value='PRESS')

        addon_keymaps.append((km, kmi))
    else:
        if prefs.debug: print('in bind_keymap: screen->view3d.move exists, activate it')#Dbg
        thekeymap.active = True

def unbind_keymap():
    if not bpy.context.window_manager.keyconfigs.addon.keymaps.get("Screen"):
        # print('GP_lock_frame: Could not found Screen addon km to unbind custom pan kmi')# Verbose-prints
        return
    if not bpy.context.window_manager.keyconfigs.addon.keymaps['Screen'].keymap_items.get('view3d.move'):
        # print('GP_lock_frame: Could not found view3d.move addon kmi in addon Screen to unbind custom pan')# Verbose-prints
        return

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    # del addon_keymaps

### keymaps/

## --- handler
# @bpy.app.handlers.persistent
@persistent
def update_state(dummy):
    prefs = get_addon_prefs()#Dbg
    scene = bpy.context.scene
    lockprop = scene.get('lockprop')
    if not lockprop:
        if prefs.debug: print('Lock property group not found')#Dbg
        return

    lockprop = scene.lockprop

    # print('bpy.context.window_manager.keyconfigs.user.keymaps: ', bpy.context.window_manager.keyconfigs.user.keymaps)
    # print("bpy.context.window_manager.keyconfigs.user.keymaps.get('3D View'):", bpy.context.window_manager.keyconfigs.user.keymaps.get('3D View'))

    if lockprop.view:
        if prefs.debug: print('LOCK ORBIT')#Dbg
        lock_orbit()
    else:
        if prefs.debug: print('UNLOCK ORBIT')#Dbg
        unlock_orbit()

    if lockprop.time:#False is ok, file loaded reset the handlers
        if prefs.debug: print('LOCK TIME')#Dbg
        scene.lockprop.holdframe = scene.frame_current
        if not lock_time_handle.__name__ in [hand.__name__ for hand in bpy.app.handlers.frame_change_pre]:
            bpy.app.handlers.frame_change_pre.append(lock_time_handle)
        lock_time()
    else:
        if prefs.debug: print('UNLOCK TIME')#Dbg
        unlock_time()



class PAPERMOD_repair(bpy.types.Operator):
    bl_idname = "papermod.repair"
    bl_label = "Repair lock damage"
    bl_description = "If lock frame or time as modified your pref disable them in viewport > click this button > save Prefs"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        ## Rotate
        rot = get_mouse_rotate_kmi()
        if rot:
            rot.active = True
        else:
            print("could not found bpy.context.window_manager.keyconfigs.user.keymaps['3D View'] 'view3d.rotate' ")

        if bpy.context.window_manager.keyconfigs.addon.keymaps.get('Screen'):
            second_pan = bpy.context.window_manager.keyconfigs.addon.keymaps['Screen'].keymap_items.get('view3d.move')
            if second_pan:
                second_pan.active = False

        ## Play
        play = bpy.context.window_manager.keyconfigs.user.keymaps['Frames'].keymap_items.get('screen.animation_play')
        if play:
            play.active = True
        else:
            print("not found: bpy.context.window_manager.keyconfigs.user.keymaps['Frames'].keymap_items.get('screen.animation_play')")

        if bpy.context.window_manager.keyconfigs.addon.keymaps.get('Window'):
            spacebar_move = bpy.context.window_manager.keyconfigs.addon.keymaps['Window'].keymap_items.get('view3d.move')
            if spacebar_move:
                spacebar_move.active = False
        
        if bpy.context.window_manager.keyconfigs.addon.keymaps.get('Grease Pencil'):
            spacebar_move = bpy.context.window_manager.keyconfigs.addon.keymaps['Grease Pencil'].keymap_items.get('view3d.move')
            if spacebar_move:
                spacebar_move.active = False

        return {"FINISHED"}

## addonprefs
class PAPERMOD_prefs(bpy.types.AddonPreferences):
    bl_idname = __name__.split('.')[0]
    
    debug : bpy.props.BoolProperty(name="Debug", description="Dev tool to print debugging messages", default=False)#Dbg


    ## tabs
    def draw(self, context):
        layout = self.layout## random color
        # layout.use_property_split = True
        col = layout.column()
        col.label(text='/!\ You do not want to save your user-prefs with the locks ON')
        col.label(text='Always disable them before saving prefs (they affect the keymap)')
        layout.separator()
        layout.label(text='Repair help:')
        col = layout.column()
        col.label(text='If the locks have "broken" your navigation and play shortcuts:')
        col.label(text='- Disable the locks')
        row = col.row()
        row.label(text='- Use the "repair" button -->')
        row.operator('papermod.repair')
        col.label(text='- Try the shortcuts...')
        col.label(text='- If Ok, save your userprefs')
        layout.prop(self, 'debug', text='Debug messages in console')#Dbg


## --- properties

class PAPERMOD_PGT_props(bpy.types.PropertyGroup):
    view : bpy.props.BoolProperty(name="lock view", description="Activate view locking", default=False)
    time : bpy.props.BoolProperty(name="lock time", description="Tell if locked or not", default=False)
    holdframe : bpy.props.IntProperty(name="locked frame", description="Keep frame number to lock")

### --- REGISTER ---

classes = (
PAPERMOD_lock_time,
PAPERMOD_lock_view,
PAPERMOD_repair,

# PAPERMOD_toolpanel,
# PAPERMOD_MT_warning,
PAPERMOD_prefs,
PAPERMOD_PGT_props,
)

def register():
    # print('\n++++++++++++++++ REGISTER')
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_HT_header.append(papermod_lock_buttons_UI)
    bpy.types.Scene.lockprop = bpy.props.PointerProperty(type = PAPERMOD_PGT_props)
    bpy.app.handlers.load_post.append(update_state)

    ## context impossible to access in there (restricted context)
    # update_state('dummy')
    # bpy.context.window_manager.keyconfigs.user.keymaps.get('3D View') not found here (must be created at the end of load...)
    # print('User view rotate active : ', bpy.context.window_manager.keyconfigs.user.keymaps.get('3D View').keymap_items['view3d.rotate'].active)
    
    # if context.scene.lockprop.view:
    #     lock_orbit()
    # print('++++++ END REGISTER\n')

def unregister():
    # print('\n--------------- UNREGISTER')
    bpy.app.handlers.load_post.remove(update_state)
    unlock_orbit()#reactivate original settings before disabling
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_HT_header.remove(papermod_lock_buttons_UI)
    unbind_keymap()
    unbind_time_keymap()
    del bpy.types.Scene.lockprop
    # print('----- END UNREGISTER\n')

if __name__ == "__main__":
    register()