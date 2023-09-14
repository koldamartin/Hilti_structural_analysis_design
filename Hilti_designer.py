
import tkinter as tk
import tkinter.font as tkFont
from tkinter import messagebox
from os import startfile
import os
import sys
import math
dir = os.path.join(os.path.dirname(__file__), "Engine")
sys.path.append(dir)
import beams
import wind

class Backend:
    def __init__(self, app_instance):
        self.app_instance = app_instance
    
    def process_button_click(self):
        width_e14 = float(self.app_instance.entry_width.get())
        depth_e15 = float(self.app_instance.entry_depth.get())
        height_e16 = float(self.app_instance.entry_height.get())
        self_wght_e31 = float(self.app_instance.entry_unit_weight.get())
        structure_wght_e32 = float(self.app_instance.entry_structure_weight.get())
        if self.app_instance.entry_chosen_weight.get() == "":
            extra_load_e38 = ""
        else:  
            extra_load_e38 = float(self.app_instance.entry_chosen_weight.get())
        structure_hght_e40 = float(self.app_instance.entry_structure_height.get())
        building_height = float(self.app_instance.entry_wind_height.get())
        wind_area_input = self.app_instance.GListBox_653.get(self.app_instance.GListBox_653.curselection())
        wind_category = self.app_instance.GListBox_383.get(self.app_instance.GListBox_383.curselection())
        eps_str = int(self.app_instance.eps_strength.get())
        
        # _____ load area_____
        load_area_e20 = width_e14 * height_e16

        # _____ ratio_____
        if width_e14 >= height_e16:
            ratio_e21 = depth_e15 / height_e16
        else:
            ratio_e21 = depth_e15 / width_e14

        # _____ force coefficient for rectangular section_____
        def force_coefficient_e22():
            if ratio_e21 <= 0.2:
                return 2
            elif ratio_e21 <= 0.7:
                return 2 + ((math.log10(5*ratio_e21))*0.4/math.log10(3.5))
            elif ratio_e21 <= 5:
                return 2.4 - ((math.log10(10/7*ratio_e21))*1.4/math.log10(50/7))
            elif ratio_e21 <= 10:
                return 1 - ((math.log10(0.2*ratio_e21))*0.1/math.log10(2))
            else:
                return 0.9

        # _____ slenderness_____
        def slenderness_e23():
            if width_e14 >= height_e16:
                return min(2*width_e14/height_e16, 70)
            else:
                return min(2*height_e16/width_e14, 70)

        # _____ coefficient of final effect___
        def final_coef_e24():
            if slenderness_e23() <= 10:
                return 0.6 + math.log10(slenderness_e23())*0.1
            else:
                return 0.7 + (math.log10(slenderness_e23()/10)*0.215/math.log10(7))

        # _____ wind pressure___
        site = wind.Site(wind.wind_area[wind_area_input], wind_category,)
        wind_pressure_e25 = site.qp(building_height)

        # _____ wind forces___
        fw_design_e26 = load_area_e20 * force_coefficient_e22() * final_coef_e24() * wind_pressure_e25/1000 * 1.5
        fw_char_e27 = fw_design_e26 / 1.5

        # _____ movement check_____
        shear_coeff_e33 = 0.78
        min_extra_load_e34 = fw_design_e26 / shear_coeff_e33 - (self_wght_e31 + structure_wght_e32)
        if min_extra_load_e34 < 0:
            min_extra_load_e34 = 0  


        # _____ flip over check_____
        def min_columns_dstnc(extra_load):
            if extra_load == "":
                extra_load = min_extra_load_e34
            total_wght_e39 = self_wght_e31 + structure_wght_e32 + extra_load
            grvt_center_e41 = structure_hght_e40 + height_e16/2
            rotation_dstnc_e42 = fw_design_e26 * grvt_center_e41 / total_wght_e39
            min_columns_dstnc_e43 = 2 * rotation_dstnc_e42
            return min_columns_dstnc_e43   
              
        def uls_check(MEd, span): #potrebuju tady vubec promennou span? podle me ji muzu smazat
            section_list = ""
            utilization_list = ""
            for section in beams.permtion_modulus:
                beam = beams.Beam(section, span)
                utilization = round(MEd / beam.permissable_moment * 100)
                section_list += f"{section}\n"
                utilization_list += f"{utilization} %\n"
            return (section_list, utilization_list)
        
        def sls_check(utilization_type, beam_dimension):
            utilization_list = ""
            for section in beams.permtion_modulus:
                if utilization_type == "A":
                    beam = beams.Beam(section, beam_dimension)
                    deformation = beam.deflection_perpendicular(depth=depth_e15, self_weight=self_weight_1, vertical_wind=wind_vert)
                elif utilization_type == "B":
                    beam = beams.Beam(section, beam_dimension)
                    deformation = beam.deflection_parallel(vert_cont + self_wght_cont)
                elif utilization_type == "C":
                    beam = beams.Beam(section, beam_dimension)
                    deformation = beam.deflection_parallel(load_continuous/1.4)
                elif utilization_type == "D":
                    beam = beams.Beam(section, beam_dimension)
                    deformation = beam.deflection_continous_3(vert_cont + self_wght_cont)
                elif utilization_type == "E":
                    beam = beams.Beam(section, beam_dimension)
                    deformation = beam.deflection_continous_4(vert_cont + self_wght_cont)
                else:
                    raise ValueError("Invalid utilization type")

                utilization = round(deformation / (beam.deformation_limit * 1000) * 100)
                utilization_list += f"{utilization} %\n"

            return utilization_list

        def load_cont_A(main_beam_length): #main_beam_length je delka nosniku na kterych jednotka primo lezi
            a = self_wght_e31 / 2 * 1.35 #pulka vlastni tihy jednotky * 1.35
            b = fw_char_e27 * height_e16 / 2 / depth_e15 *1.5 #vertikalni sila od vetru *1.5
            x1 = (main_beam_length - depth_e15)/2
            x2 = x1 + depth_e15
            R1 = (a*x2 + b*x2 + a*x1 - b*x1)/main_beam_length #reaction in kN
            span = structure_width
            return R1 / span #reaction in kN/m         
        
        def punching_check(extra_load, supports_number = 4):
            if extra_load == "":
                extra_load = min_extra_load_e34
            utilization = ((extra_load + self_wght_e31 + structure_wght_e32)/supports_number)/(0.25*0.3*eps_str/5)*100
            return f"{(round(utilization))} %"
        
        def MEd_perpendicular(span, vert_force):
            a = (span - depth_e15) / 2
            MEd_self_weight = self_weight_1 * 1.35 * a
            MEd_wind = vert_force * 1.5 * depth_e15 / span * a
            return MEd_wind + MEd_self_weight
            
        def get_span():
            if self.app_instance.entry_chosen_span.get() == "":
                return structure_depth
            else:
                return float(self.app_instance.entry_chosen_span.get())
            
        structure_depth = max(depth_e15 + 0.2, min_columns_dstnc(extra_load_e38))
        structure_depth = get_span()
        structure_width = width_e14 + 0.3
        
        self.app_instance.label_extra_wght.config(text = round(min_extra_load_e34, 2))
        self.app_instance.label_min_span.config(text = round(structure_depth, 2))
        
        try:
            if position_choice == 1:
                beams_number_e47 = int(self.app_instance.entry_type_A.get())
                if beams_number_e47 == 1:
                    raise Exception("Jednotka nesmí ležet jen na jednom nosníku!")
                elif beams_number_e47 == 2:
                    horiz_force_edge_e48 = fw_char_e27 / beams_number_e47
                    horiz_force_mid_e49 = 0
                    horiz_force_mid_e56 = 0
                    vert_force_mid_e57 = 0
                    self_weight_edge = self_wght_e31 / 4
                    self_weight_mid = 0
                else:
                    horiz_force_edge_e48 = fw_char_e27 / (beams_number_e47 - 1) / 2
                    horiz_force_mid_e49 = fw_char_e27 / (beams_number_e47 - 1)
                    horiz_force_mid_e56 = horiz_force_mid_e49 / 2
                    vert_force_mid_e57 = horiz_force_mid_e49 * height_e16 / 2 / depth_e15
                    self_weight_edge = self_wght_e31 / (beams_number_e47 - 1) / 2 / 2
                    self_weight_mid = self_wght_e31 / (beams_number_e47 - 1) / 2
                horiz_force_edge_e52 = horiz_force_edge_e48 / 2
                vert_force_edge_e53 = horiz_force_edge_e48 * height_e16 / 2 / depth_e15
                # Forces to export
                self_weight_1 = max(self_weight_mid, self_weight_edge)  # kN
                wind_vert = max(vert_force_edge_e53, vert_force_mid_e57)  # kN
                wind_horiz = max(horiz_force_edge_e52, horiz_force_mid_e56)  # kN

                # Výpočet hlavních nosníků - perpendicular
                MEd_perp = MEd_perpendicular(structure_depth, wind_vert)

                # Výpočet vedlejších nosníků - parallel
                load_continuous = load_cont_A(structure_depth)
                MEd_parallel = 1/8 * load_continuous * structure_width**2

                self.app_instance.label_sections_1.config(text= uls_check(MEd_perp, structure_depth)[0])     
                self.app_instance.label_sections_2.config(text= uls_check(MEd_parallel, structure_width)[0])  
                self.app_instance.label_uls_1.config(text= uls_check(MEd_perp, structure_depth)[1])
                self.app_instance.label_uls_2.config(text = uls_check(MEd_parallel, structure_width)[1])
                self.app_instance.label_sls_1.config(text= sls_check("A", structure_depth))
                self.app_instance.label_sls_2.config(text = sls_check("C", structure_width))
                self.app_instance.label_eps.config(text = punching_check(extra_load_e38))

            elif position_choice == 2:
                # Výpočet hlavních nosníků - parallel
                vert_cont = fw_char_e27 * height_e16 / 2 / depth_e15 / structure_width  # kN/m
                self_wght_cont = self_wght_e31 / 2 / structure_width  # kN/m 
                #  Bending moment calculation - SPOCITAT PRESNEJC, takhle to vychazi blbe
                MEd_parallel = 1 / 8 * (vert_cont * 1.5 + self_wght_cont * 1.35) * structure_width ** 2  # kNm

                # Výpočet vedlejších nosníků - perpendicular
                self_weight_1 = self_wght_e31 / 4
                wind_vert = (fw_char_e27 / 2) * height_e16 / 2 / depth_e15 
                MEd_perp = MEd_perpendicular(structure_depth, wind_vert)

                self.app_instance.label_sections_1.config(text = uls_check(MEd_parallel, structure_width)[0])
                self.app_instance.label_sections_2.config(text= uls_check(MEd_perp, structure_depth)[0])         
                self.app_instance.label_uls_1.config(text = uls_check(MEd_parallel, structure_width)[1])
                self.app_instance.label_uls_2.config(text = uls_check(MEd_perp, structure_depth)[1])
                self.app_instance.label_sls_1.config(text = sls_check("B", structure_width))
                self.app_instance.label_sls_2.config(text = sls_check("A", structure_depth))
                self.app_instance.label_eps.config(text = punching_check(extra_load_e38))

            elif position_choice == 3:
                beams_number_e47 = int(self.app_instance.entry_type_C.get())
                if not beams_number_e47 > 2:
                    messagebox.showwarning(title="Warning", message="Počet nosníků musí být 3 nebo víc!")
                else:
                    horiz_force_edge_e48 = fw_char_e27 / (beams_number_e47 - 1) / 2
                    horiz_force_mid_e49 = fw_char_e27 / (beams_number_e47 - 1)
                    horiz_force_mid_e56 = horiz_force_mid_e49 / 2
                    vert_force_mid_e57 = horiz_force_mid_e49 * height_e16 / 2 / depth_e15
                    self_weight_edge = self_wght_e31 / (beams_number_e47 - 1) / 2 / 2
                    self_weight_mid = self_wght_e31 / (beams_number_e47 - 1) / 2
                    horiz_force_edge_e52 = horiz_force_edge_e48 / 2
                    vert_force_edge_e53 = horiz_force_edge_e48 * height_e16 / 2 / depth_e15
                    # Forces to export
                    self_weight_1 = max(self_weight_mid, self_weight_edge)  # kN
                    wind_vert = max(vert_force_edge_e53, vert_force_mid_e57)  #N
                    wind_horiz = max(horiz_force_edge_e52, horiz_force_mid_e56)  # kN

                    # Výpočet hlavních nosníků - parallel
                    one_span = (structure_width) / (beams_number_e47 - 1)
                    vert_cont = fw_char_e27 * height_e16 / 2 / depth_e15 / (structure_width)  # kN/m
                    self_wght_cont = self_wght_e31 / 2 / (structure_width)  # kN/m 

                    #  Bending moment calculation 
                    if beams_number_e47 == 3:
                        MEd_parallel = 0.125 * (vert_cont * 1.5 + self_wght_cont * 1.35) * one_span ** 2  # kNm
                        self.app_instance.label_sls_1.config(text = sls_check("D", one_span))
                    elif beams_number_e47 > 3:
                        MEd_parallel = 0.1 * (vert_cont * 1.5 + self_wght_cont * 1.35) * one_span ** 2  # kNm
                        self.app_instance.label_sls_1.config(text = sls_check("E", one_span))

                    # Výpočet vedlejších nosníků - perpendicular
                    MEd_perp = MEd_perpendicular(structure_depth, wind_vert)

                    self.app_instance.label_sections_1.config(text= uls_check(MEd_parallel, one_span)[0])  
                    self.app_instance.label_sections_2.config(text= uls_check(MEd_perp, structure_depth)[0])  
                    self.app_instance.label_uls_1.config(text = uls_check(MEd_parallel, one_span)[1])
                    self.app_instance.label_uls_2.config(text = uls_check(MEd_perp, structure_depth)[1])

                    self.app_instance.label_sls_2.config(text = sls_check("A", structure_depth))
                    self.app_instance.label_eps.config(text = punching_check(extra_load_e38, supports_number = (beams_number_e47 * 2)-2))

        except NameError:
            messagebox.showerror(title="Error", message="Zvolte uložení jednotky. A/B/C!")

        print(f'Structure depth is {structure_depth} m')
        print(f'Structure width is {structure_width} m')

class App:
    def __init__(self, root):
        #setting title
        root.title("Hilti designer v.1.2 Date: 30.08.2023")
        root.state('zoomed')
        self.background = tk.PhotoImage(file="Engine\hilti_logo.png")
        
    # _____  Labels _____  
        GLabel_63=tk.Label(root)
        ft = tkFont.Font(family='Times',size=18)
        GLabel_63["justify"] = "center"
        GLabel_63["image"] = self.background
        GLabel_63.place(x=10,y=10,width=300,height=83)

        GLabel_706=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_706["font"] = ft
        GLabel_706["fg"] = "#333333"
        GLabel_706["justify"] = "center"
        GLabel_706["text"] = "Šířka jednotky [m]:"
        GLabel_706.place(x=40,y=140,width=111,height=30)

        GLabel_106=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_106["font"] = ft
        GLabel_106["fg"] = "#333333"
        GLabel_106["justify"] = "center"
        GLabel_106["text"] = "Hloubka jednotky [m]:"
        GLabel_106.place(x=40,y=170,width=127,height=30)

        GLabel_559=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_559["font"] = ft
        GLabel_559["fg"] = "#333333"
        GLabel_559["justify"] = "center"
        GLabel_559["text"] = "Výška jednotky [m]:"
        GLabel_559.place(x=40,y=200,width=109,height=30)

        GLabel_532=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_532["font"] = ft
        GLabel_532["fg"] = "#333333"
        GLabel_532["justify"] = "center"
        GLabel_532["text"] = "Tíha jednotky [kN]:"
        GLabel_532.place(x=40,y=230,width=108,height=30)

        GLabel_577=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        GLabel_577["font"] = ft
        GLabel_577["fg"] = "#333333"
        GLabel_577["justify"] = "center"
        GLabel_577["text"] = "Informace o jednotce"
        GLabel_577["relief"] = "flat"
        GLabel_577.place(x=40,y=100,width=206,height=30)

        GLabel_360=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        GLabel_360["font"] = ft
        GLabel_360["fg"] = "#333333"
        GLabel_360["justify"] = "center"
        GLabel_360["text"] = "Vítr"
        GLabel_360["relief"] = "flat"
        GLabel_360.place(x=30,y=520,width=189,height=30)

        GLabel_535=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_535["font"] = ft
        GLabel_535["fg"] = "#333333"
        GLabel_535["justify"] = "center"
        GLabel_535["text"] = "Větrná oblast"
        GLabel_535.place(x=40,y=580,width=77,height=30)

        GLabel_849=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_849["font"] = ft
        GLabel_849["fg"] = "#333333"
        GLabel_849["justify"] = "center"
        GLabel_849["text"] = "Kategorie terénu"
        GLabel_849.place(x=180,y=580,width=97,height=30)

        GLabel_140=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        GLabel_140["font"] = ft
        GLabel_140["fg"] = "#333333"
        GLabel_140["justify"] = "center"
        GLabel_140["text"] = "Informace o konstrukci"
        GLabel_140["relief"] = "flat"
        GLabel_140.place(x=70,y=280,width=159,height=30)

        GLabel_419=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_419["font"] = ft
        GLabel_419["fg"] = "#333333"
        GLabel_419["justify"] = "center"
        GLabel_419["text"] = "Tíha konstrukce [kN]:"
        GLabel_419.place(x=40,y=320,width=120,height=30)

        GLabel_725=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_725["font"] = ft
        GLabel_725["fg"] = "#333333"
        GLabel_725["justify"] = "center"
        GLabel_725["text"] = "Výška nad zemí [m]"
        GLabel_725.place(x=40,y=550,width=115,height=30)

        GLabel_17=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_17["font"] = ft
        GLabel_17["fg"] = "#333333"
        GLabel_17["justify"] = "center"
        GLabel_17["text"] = "Výška konstrukce [m]:"
        GLabel_17.place(x=40,y=410,width=124,height=30)

        GLabel_54=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_54["font"] = ft
        GLabel_54["fg"] = "#333333"
        GLabel_54["justify"] = "center"
        GLabel_54["text"] = "Min. rozpětí nosníků [m]:"
        GLabel_54.place(x=40,y=440,width=141,height=30)
        
        GLabel_281=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_281["font"] = ft
        GLabel_281["fg"] = "#333333"
        GLabel_281["justify"] = "center"
        GLabel_281["text"] = "Přepsat rozpětí nosníků [m]:"
        GLabel_281.place(x=40,y=470,width=160,height=30)

        GLabel_478=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_478["font"] = ft
        GLabel_478["fg"] = "#333333"
        GLabel_478["justify"] = "center"
        GLabel_478["text"] = "Přepsat přitížení kce [kN]:"
        GLabel_478.place(x=40,y=380,width=146,height=30)

        GLabel_403=tk.Canvas(root)
        self.bg_image_a = tk.PhotoImage(file='Engine\cypA.png')
        GLabel_403.create_image(0, 0, image=self.bg_image_a, anchor='nw')
        GLabel_403.place(x=300,y=50,width=300,height=220)

        GLabel_49=tk.Canvas(root)
        self.bg_image_b = tk.PhotoImage(file="Engine\cypB.png")
        GLabel_49.create_image(0, 0, image=self.bg_image_b, anchor='nw')
        GLabel_49.place(x=300,y=310,width=300,height=220)
        
        GLabel_667=tk.Canvas(root)
        self.bg_image_c = tk.PhotoImage(file="Engine\cypC.png")
        GLabel_667.create_image(0, 0, image=self.bg_image_c, anchor='nw')
        GLabel_667.place(x=300,y=570,width=300,height=220)

        GLabel_980=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        GLabel_980["font"] = ft
        GLabel_980["fg"] = "#333333"
        GLabel_980["justify"] = "center"
        GLabel_980["text"] = "Zvolte typ uložení jednotky:"
        GLabel_980.place(x=360,y=20,width=191,height=30)



        GLabel_406=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_406["font"] = ft
        GLabel_406["fg"] = "#333333"
        GLabel_406["justify"] = "center"
        GLabel_406["text"] = "Počet příčných nosníků:"
        GLabel_406.place(x=360,y=280,width=137,height=30)

        GLabel_492=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_492["font"] = ft
        GLabel_492["fg"] = "#333333"
        GLabel_492["justify"] = "center"
        GLabel_492["text"] = "Počet příčných rámů:"
        GLabel_492.place(x=360,y=800,width=120,height=30)

        GLabel_609=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        GLabel_609["font"] = ft
        GLabel_609["fg"] = "#333333"
        GLabel_609["justify"] = "center"
        GLabel_609["text"] = "Výsledky:"
        GLabel_609.place(x=690,y=20,width=70,height=25)

        GLabel_978=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_978["font"] = ft
        GLabel_978["fg"] = "#333333"
        GLabel_978["justify"] = "center"
        GLabel_978["text"] = "Min. přitížení kce [kN]"
        GLabel_978.place(x=40,y=350,width=120,height=30)

        GLabel_277=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_277["font"] = ft
        GLabel_277["fg"] = "#333333"
        GLabel_277["justify"] = "center"
        GLabel_277["text"] = "Hlavní nosníky"
        GLabel_277.place(x=690,y=100,width=87,height=30)
        
        GLabel_86=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_86["font"] = ft
        GLabel_86["fg"] = "#333333"
        GLabel_86["justify"] = "center"
        GLabel_86["text"] = "Vedlejší nosníky"
        GLabel_86.place(x=690,y=180,width=97,height=30)
        
        self.label_eps_result=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_eps_result["font"] = ft
        self.label_eps_result["fg"] = "#333333"
        self.label_eps_result["justify"] = "left"
        self.label_eps_result["text"] = "Protlačení střešního \nplášťě"
        self.label_eps_result.place(x=690,y=250,width=110,height=100)



        GLabel_15=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_15["font"] = ft
        GLabel_15["fg"] = "#333333"
        GLabel_15["justify"] = "center"
        GLabel_15["text"] = "Průřez"
        GLabel_15.place(x=820,y=40,width=41,height=30)

        GLabel_892=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_892["font"] = ft
        GLabel_892["fg"] = "#333333"
        GLabel_892["justify"] = "center"
        GLabel_892["text"] = "Využití MSÚ [%]"
        GLabel_892.place(x=950,y=40,width=90,height=30)

        self.label_sections_1=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_sections_1["font"] = ft
        self.label_sections_1["fg"] = "#333333"
        self.label_sections_1["justify"] = "center"
        self.label_sections_1["text"] = "section 1"
        self.label_sections_1.place(x=820,y=70,width=61,height=100)
        
        self.label_sections_2=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_sections_2["font"] = ft
        self.label_sections_2["fg"] = "#333333"
        self.label_sections_2["justify"] = "center"
        self.label_sections_2["text"] = "section 2"
        self.label_sections_2.place(x=820,y=150,width=61,height=100)
        
        self.label_3=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_3["font"] = ft
        self.label_3["fg"] = "#333333"
        self.label_3["justify"] = "center"
        self.label_3["text"] = "MT-B-LDP-ME"
        self.label_3.place(x=840,y=280,width=81,height=25)
        
        self.label_eps=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_eps["font"] = ft
        self.label_eps["fg"] = "#333333"
        self.label_eps["justify"] = "center"
        self.label_eps["text"] = "n eps"
        self.label_eps.place(x=940,y=280,width=61,height=25)

        self.GLabel_569=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.GLabel_569["font"] = ft
        self.GLabel_569["fg"] = "#333333"
        self.GLabel_569["justify"] = "center"
        self.GLabel_569["text"] = 'Pevnost EPS při \n10% stlačení [kPa]'
        self.GLabel_569.place(x=40,y=720,width=100,height=60)

        self.label_uls_1=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_uls_1["font"] = ft
        self.label_uls_1["fg"] = "#333333"
        self.label_uls_1["justify"] = "center"
        self.label_uls_1["text"] = "n uls 1"
        self.label_uls_1.place(x=930,y=70,width=70,height=100)
        
        self.label_uls_2=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_uls_2["font"] = ft
        self.label_uls_2["fg"] = "#333333"
        self.label_uls_2["justify"] = "center"
        self.label_uls_2["text"] = "n uls 2"
        self.label_uls_2.place(x=930,y=150,width=70,height=100)


        GLabel_873=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        GLabel_873["font"] = ft
        GLabel_873["fg"] = "#333333"
        GLabel_873["justify"] = "center"
        GLabel_873["text"] = "Využití MSP [%]"
        GLabel_873.place(x=1100,y=40,width=90,height=30)

        self.label_sls_1=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_sls_1["font"] = ft
        self.label_sls_1["fg"] = "#333333"
        self.label_sls_1["justify"] = "center"
        self.label_sls_1["text"] = "n sls 1"
        self.label_sls_1.place(x=1100,y=70,width=70,height=100)
        
        self.label_sls_2=tk.Label(root)
        ft = tkFont.Font(family='Times',size=10)
        self.label_sls_2["font"] = ft
        self.label_sls_2["fg"] = "#333333"
        self.label_sls_2["justify"] = "center"
        self.label_sls_2["text"] = "n sls 2"
        self.label_sls_2.place(x=1100,y=150,width=70,height=100)
        

    # _____  Buttons _____  
        GButton_99=tk.Button(root)
        GButton_99["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=18)
        GButton_99["font"] = ft
        GButton_99["bg"] = "green"
        GButton_99["justify"] = "center"
        GButton_99["text"] = "Spočítej"
        GButton_99["relief"] = "raised"
        GButton_99.place(x=680,y=720,width=370,height=60)
        GButton_99["command"] = self.GButton_99_command
        
        Gbutton_help = tk.Button(root)
        Gbutton_help["text"] = "Help"
        ft = tkFont.Font(family='Times',size=12)
        Gbutton_help["font"] = ft
        Gbutton_help["justify"] = "center"
        Gbutton_help["relief"] = "raised"
        Gbutton_help.place(x=680,y=650,width=250,height=40)
        Gbutton_help["command"] = self.open_file
       
    # _____  Entries _____  
        self.entry_width=tk.Entry(root)
        self.entry_width["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_width["font"] = ft
        self.entry_width["fg"] = "#333333"
        self.entry_width["justify"] = "center"
        self.entry_width.insert(0,"0.9")
        self.entry_width.place(x=210,y=140,width=70,height=25)
        
        self.entry_depth=tk.Entry(root)
        self.entry_depth["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_depth["font"] = ft
        self.entry_depth["fg"] = "#333333"
        self.entry_depth["justify"] = "center"
        self.entry_depth.insert(0,"0.32")
        self.entry_depth.place(x=210,y=170,width=70,height=25)
        
        self.entry_height=tk.Entry(root)
        self.entry_height["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_height["font"] = ft
        self.entry_height["fg"] = "#333333"
        self.entry_height["justify"] = "center"
        self.entry_height.insert(0,"1.4")
        self.entry_height.place(x=210,y=200,width=70,height=25)
        
        self.entry_unit_weight=tk.Entry(root)
        self.entry_unit_weight["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_unit_weight["font"] = ft
        self.entry_unit_weight["fg"] = "#333333"
        self.entry_unit_weight["justify"] = "center"
        self.entry_unit_weight.insert(0,"2")
        self.entry_unit_weight.place(x=210,y=230,width=70,height=25)
                
        self.entry_structure_weight=tk.Entry(root)
        self.entry_structure_weight["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_structure_weight["font"] = ft
        self.entry_structure_weight["fg"] = "#333333"
        self.entry_structure_weight["justify"] = "center"
        self.entry_structure_weight.insert(0,"0.4")
        self.entry_structure_weight.place(x=210,y=320,width=70,height=25)

        self.label_extra_wght=tk.Label(root)
        self.label_extra_wght["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.label_extra_wght["font"] = ft
        self.label_extra_wght["fg"] = "#333333"
        self.label_extra_wght["justify"] = "center"
        self.label_extra_wght["text"] = "..."
        self.label_extra_wght.place(x=210,y=350,width=70,height=25)
        
        self.entry_chosen_weight=tk.Entry(root)
        self.entry_chosen_weight["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_chosen_weight["font"] = ft
        self.entry_chosen_weight["fg"] = "#333333"
        self.entry_chosen_weight["justify"] = "center"
        self.entry_chosen_weight.place(x=210,y=380,width=70,height=25)
        
        self.entry_structure_height=tk.Entry(root)
        self.entry_structure_height["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_structure_height["font"] = ft
        self.entry_structure_height["fg"] = "#333333"
        self.entry_structure_height["justify"] = "center"
        self.entry_structure_height.insert(0,"0.5")
        self.entry_structure_height.place(x=210,y=410,width=70,height=25)
        
        self.label_min_span=tk.Label(root)
        self.label_min_span["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.label_min_span["font"] = ft
        self.label_min_span["fg"] = "#333333"
        self.label_min_span["justify"] = "center"
        self.label_min_span["text"] = "..."
        self.label_min_span.place(x=210,y=440,width=70,height=25)
        
        self.entry_chosen_span=tk.Entry(root)
        self.entry_chosen_span["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_chosen_span["font"] = ft
        self.entry_chosen_span["fg"] = "#333333"
        self.entry_chosen_span["justify"] = "center"
        self.entry_chosen_span.insert(0,"")
        self.entry_chosen_span.place(x=210,y=470,width=70,height=25)
        
        self.entry_wind_height=tk.Entry(root)
        self.entry_wind_height["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_wind_height["font"] = ft
        self.entry_wind_height["fg"] = "#333333"
        self.entry_wind_height["justify"] = "center"
        self.entry_wind_height.insert(0,"15")
        self.entry_wind_height.place(x=210,y=550,width=70,height=25)
                                              
        self.entry_type_A=tk.Entry(root)
        self.entry_type_A["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_type_A["font"] = ft
        self.entry_type_A["fg"] = "#333333"
        self.entry_type_A["justify"] = "center"
        self.entry_type_A.insert(0,"2")
        self.entry_type_A.place(x=510,y=280,width=70,height=25)
        
        self.entry_type_C=tk.Entry(root)
        self.entry_type_C["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.entry_type_C["font"] = ft
        self.entry_type_C["fg"] = "#333333"
        self.entry_type_C["justify"] = "center"
        self.entry_type_C.insert(0,"3")
        self.entry_type_C.place(x=510,y=800,width=70,height=25)
        
        self.eps_strength=tk.Entry(root)
        self.eps_strength["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.eps_strength["font"] = ft
        self.eps_strength["fg"] = "#333333"
        self.eps_strength["justify"] = "center"
        self.eps_strength.insert(0,"150")
        self.eps_strength.place(x=200,y=740,width=70,height=25)
        
 
     # _____  Radiobuttons _____          
        self.radio = tk.IntVar()
        
        GRadio_19=tk.Radiobutton(root)
        ft = tkFont.Font(family='Times',size=10)
        GRadio_19["font"] = ft
        GRadio_19["fg"] = "#333333"
        GRadio_19["justify"] = "center"
        GRadio_19["text"] = "Typ A"
        GRadio_19.place(x=600,y=160,width=85,height=25)
        GRadio_19["variable"] = self.radio
        GRadio_19["value"] = 1
        GRadio_19["command"] = self.GRadio_19_command

        GRadio_840=tk.Radiobutton(root)
        ft = tkFont.Font(family='Times',size=10)
        GRadio_840["font"] = ft
        GRadio_840["fg"] = "#333333"
        GRadio_840["justify"] = "center"
        GRadio_840["text"] = "Typ B"
        GRadio_840.place(x=600,y=420,width=85,height=25)
        GRadio_840["variable"] = self.radio
        GRadio_840["value"] = 2
        GRadio_840["command"] = self.GRadio_840_command

        GRadio_67=tk.Radiobutton(root)
        ft = tkFont.Font(family='Times',size=10)
        GRadio_67["font"] = ft
        GRadio_67["fg"] = "#333333"
        GRadio_67["justify"] = "center"
        GRadio_67["text"] = "Typ C"
        GRadio_67.place(x=600,y=680,width=85,height=25)
        GRadio_67["variable"] = self.radio
        GRadio_67["value"] = 3
        GRadio_67["command"] = self.GRadio_67_command
        
    # _____  Listboxes _____         
        self.GListBox_653=tk.Listbox(root)
        self.GListBox_653["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.GListBox_653["font"] = ft
        self.GListBox_653["fg"] = "#333333"
        self.GListBox_653["justify"] = "center"
        self.GListBox_653.place(x=40,y=610,width=68,height=103)
        self.GListBox_653["exportselection"] = "0"
        area_list = ['I', 'II', 'III', 'IV', 'V']
        var1 = tk.Variable(value=area_list)
        self.GListBox_653["listvariable"] = var1
        self.GListBox_653["selectmode"] = "single"
        self.GListBox_653["setgrid"] = "True"
        self.GListBox_653.select_set(0)
        
        self.GListBox_383=tk.Listbox(root)
        self.GListBox_383["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=10)
        self.GListBox_383["font"] = ft
        self.GListBox_383["fg"] = "#333333"
        self.GListBox_383["justify"] = "center"
        self.GListBox_383.place(x=180,y=610,width=66,height=103)
        category_list = ['I', 'II', 'III', 'IV']
        var2 = tk.Variable(value=category_list)
        self.GListBox_383["listvariable"] = var2
        self.GListBox_383["selectmode"] = "single"
        self.GListBox_383.select_set(0)
        self.GListBox_383['exportselection'] = False
        
        # set the disable_entry function to be called when a radiobutton is selected
        self.radio.trace('w', lambda *args: self.disable_entry())     
        
        self.backend = Backend(self) # Create an backend object from Backend Class
       
    def disable_entry(self):
        selected = self.radio.get()
        if selected == 3:
            self.entry_type_C.config(state="normal")
            self.entry_type_A.config(state="disabled")
        elif selected == 2:
            self.entry_type_C.config(state="disabled")
            self.entry_type_A.config(state="disabled")
        elif selected == 1:
            self.entry_type_C.config(state="disabled")
            self.entry_type_A.config(state="normal")
            
    def open_file(self):
        filename = startfile("Engine\help.txt")

    def GRadio_19_command(self):
        global position_choice
        position_choice = 1


    def GRadio_840_command(self):
        global position_choice
        position_choice = 2


    def GRadio_67_command(self):
        global position_choice
        position_choice = 3

        
    def GButton_99_command(self):
        self.backend.process_button_click()

             
#if __name__ == "__main__":
root = tk.Tk()
app = App(root)
root.mainloop()

#TODO sníh, dvouosy ohyb na vedlejsi nosniky, vyskakovaci chybova okna, zjednodusit kod, export artiklovych cisel (ulozit jpg), obrazky, otestovat
#TODO vybarvit vysledky a pridat k nim checkmarky
#TODO tlacitko co ukaze vetrnou mapu
#TODO pro MT-40D posudek na smyk

#In the code example I provided, the Backend class is not inheriting from the App class.
# It's a separate class that collaborates with the App class to handle the button click functionality and data processing.
# Inheritance is not used here because it seems that you want to encapsulate the button click processing into a separate class
# that is not a specialized version of the App class.

# Verze 1.0 - initial release
# Verze 1.1 - přidány 3D obrázky
# Verze 1.2 - Přidána Backend Class. Přidán Error messagebox pokud není vybrán typ uložení
