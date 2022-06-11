import bpy
from bpy.props import PointerProperty


class TestPanel(bpy.types.Panel):
	bl_label = "Hedgehog Level Editor"
	bl_idname = "HLE_PT_TestPanel"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Hedgehog Level Editor"

	def draw(self, context):
		layout = self.layout
		scene = context.scene

		row = layout.row()
		row.label(text="Design Tools", icon="CUBE")
		row = layout.row()
		row.operator("hle.draw_layout_w_gp")
		row = layout.row()
		row.operator("hle.generate_level")
		row = layout.row()
		row.prop(scene, "layout")
		row = layout.row()
		row.prop(scene, "terrain")
		


class HLE_OT_draw_layout_w_gp(bpy.types.Operator):
	bl_idname = "hle.draw_layout_w_gp"
	bl_label = "Draw Layout"

	def execute(self, context):
		
		#checking for legal mode, if not sets object mode
		if not bpy.context.object is None:
			bpy.ops.object.mode_set(mode="OBJECT")
			
		#adding the gp as new obj
		bpy.ops.object.gpencil_add(radius=1, location=(0, 0, 0), type="EMPTY")
		
		#setting name in var
		name = 'Draw_Layout.000'
		#getting the active object (newly created obj) 
		obj = bpy.context.active_object
		#changing the name of active
		obj.name = name
		
		#setting new gp to active
		#bpy.context.view_layer.objects.active = obj
		#setting new gp to selected
		#bpy.data.objects[name].select_set(True)

		#Setting the camera to ortho top view   	
		bpy.ops.view3d.view_axis(type='TOP')
		
		#toggling to draw mode
		bpy.ops.gpencil.paintmode_toggle()
		
		return {"FINISHED"}

class HLE_OT_generate_level(bpy.types.Operator):
	bl_idname = "hle.generate_level"
	bl_label = "Generate Level"
	

	#Excutes the op (inbuilt)
	def execute(self, context):
		
		#These were outside before, but work in here
		#function for safely setting object mode
		def safe_set_obj_mode():
			if not bpy.context.object is None:
				bpy.ops.object.mode_set(mode="OBJECT")
			return
			
		#function for exclusive selection
		def selEx(name):
			safe_set_obj_mode()
			obj = bpy.data.objects[name]
			bpy.ops.object.select_all(action='DESELECT')
			context.view_layer.objects.active = obj
			obj.select_set(True)
			
		#function for deselection   
		def desel():
			safe_set_obj_mode()
			bpy.ops.object.select_all(action='DESELECT')
			return

		def showMsgBox(message = "", title = "Message Box", icon = 'INFO'):
			def draw(self, context):
				self.layout.label(text=message)
			bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
				
		#Sets var
		scene = context.scene
		
		layout = scene.layout
		terrain = scene.terrain
		
		#Checks for legal layout, Does it exist? is it GP?
		if layout is None or layout.type != "GPENCIL":
			showMsgBox(message="Please select a valid Grease Pencil Layout", title = "Invalid Layout Selection", icon = "ERROR")
			return {"INTERFACE"}#Handled, not executed

		#Checks for legal terrain, Does it exist? is it Mesh?
		if terrain is None or terrain.type != "MESH":
			showMsgBox(message="Please select a valid Mesh Terrain", title = "Invalid Terrain Selection", icon = "ERROR")
			return {"INTERFACE"}#Handled, not executed


		#ExSelects the layout
		selEx(layout.name)  
		
		#Joins gp strokes
		bpy.ops.gpencil.editmode_toggle()
		bpy.ops.gpencil.select_all(action='SELECT')
		bpy.ops.gpencil.stroke_join()
		
		#Converts to curve
        #sets mode to object mode to do this
		bpy.ops.object.mode_set(mode="OBJECT")

		#line belowe not needed 		
		#bpy.ops.object.convert(target='CURVE')
		bpy.ops.gpencil.convert(type='POLY', use_timing_data=False)
		
		#The gp is the only object selected at this point
		#Thus the 2nd selected object will be the curve
		#Sets name of layout curve
		bpy.context.selected_objects[1].name = "Lvl_Curve_Tmp"


		#Generation Steps
		#ExSelects the layout curve
		selEx("Lvl_Curve_Tmp")  
		#Sets the cursor to the curve
		bpy.ops.view3d.snap_cursor_to_selected()
		#ExSelects the terrain curve
		selEx(terrain.name)
		#Sets selected to cursor
		bpy.ops.view3d.snap_selected_to_cursor(use_offset=False)
		
		#The terrain is selected
		
		#Adds modifiers to terrain
		#Array modifier and settings
		bpy.context.object.modifiers.new('hle_mod_arr', type='ARRAY')
		bpy.context.object.modifiers["hle_mod_arr"].fit_type = 'FIT_CURVE'
		bpy.context.object.modifiers["hle_mod_arr"].curve = bpy.data.objects["Lvl_Curve_Tmp"]
		#Curve modifier and settings
		bpy.context.object.modifiers.new('hle_mod_crv', type='CURVE')
		bpy.context.object.modifiers["hle_mod_crv"].object = bpy.data.objects["Lvl_Curve_Tmp"]
		
		#ExSelects the layout curve
		selEx("Lvl_Curve_Tmp")
		#Sets to Edit mode
		bpy.ops.object.editmode_toggle()
		#Selects all vertices
		bpy.ops.curve.select_all(action='SELECT')
		#Fixes the mean radius
		bpy.ops.curve.radius_set(radius=1.0)
		#sets back to object mode
		bpy.ops.object.editmode_toggle()
		
		#Apply modifiers after selecting the terrain
		selEx(terrain.name)
		bpy.ops.object.modifier_apply(modifier="hle_mod_arr")
		bpy.ops.object.modifier_apply(modifier="hle_mod_crv")
		
		#ExSelects the layout curve
		selEx("Lvl_Curve_Tmp")
		#Delete the Tmp Curve at the end
		bpy.ops.object.delete()
		
		return {"FINISHED"}

classes = [TestPanel, HLE_OT_draw_layout_w_gp, HLE_OT_generate_level]


def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	bpy.types.Scene.layout = PointerProperty(type=bpy.types.Object)
	bpy.types.Scene.terrain = PointerProperty(type=bpy.types.Object)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)


if __name__ == "__main__":
	register()