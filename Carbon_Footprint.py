import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
from datetime import datetime
import os

# --------------------------------------------------------
# 1. Emission Factors & Constants
# --------------------------------------------------------
EMISSION_FACTORS = {
    "Car": 0.2, "Bus": 0.05, "Train": 0.03, "Motorcycle": 0.15, "Walk_Bike": 0.0,
    "Energy_Factor": 0.4, 
    "Food": 2.5,         
}

ENERGY_ESTIMATION = {
    "Tablet_Devices": 0.05, "Large_Appliances": 2.0, "Lighting_Bulbs": 0.015,
    "Small_Devices": 0.5, "Average_Usage_Hours": 6,
}

CO2_PER_TREE_PER_YEAR = 25  
DAYS_IN_MONTH = 30.43      

# --- UPDATED: Carbon Tax Price in EGP ---
# Price in Egyptian Pounds per kg of CO2 (Hypothetical value)
CARBON_TAX_PER_KG = 2.5  

# UI Colors
PRIMARY_COLOR = "#1ABC9C" 
ACCENT_COLOR = "#E74C3C"   
BACKGROUND_COLOR = "gray10"
FRAME_COLOR = "gray17"

# --------------------------------------------------------
# 2. Main Carbon Footprint Calculator Application
# --------------------------------------------------------

class SimplifiedCarbonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.daily_co2 = 0.0
        self.title("Carbon Footprint Calculator")
        self.geometry("650x700") 
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green") 
        
        self.transport_co2 = ctk.DoubleVar(value=0.0)
        self.energy_val = ctk.DoubleVar(value=0.0) 
        self.food_var = ctk.StringVar(value="0") 
        self.energy_direct_var = ctk.StringVar(value="0") 

        self.create_splash_screen()

    # --- Splash Screen (Unchanged) ---
    def create_splash_screen(self):
        self.splash_frame = ctk.CTkFrame(self, fg_color=BACKGROUND_COLOR)
        self.splash_frame.pack(fill="both", expand=True)

        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            logo_path = os.path.join(current_dir, "carbon_logo.png") 
            logo_image = ctk.CTkImage(Image.open(logo_path), size=(150, 150)) 
            ctk.CTkLabel(self.splash_frame, image=logo_image, text="").pack(pady=(50, 10))
        except:
            ctk.CTkLabel(self.splash_frame, text="[Logo Placeholder]", font=ctk.CTkFont(size=16), text_color="red").pack(pady=(50, 10))

        title_text = "Welcome to J.A.R.V.I.S.\n(Your Carbon Assistant)"
        ctk.CTkLabel(self.splash_frame, text=title_text, 
                     font=ctk.CTkFont(family="Arial", size=26, weight="bold"), 
                     text_color=PRIMARY_COLOR, justify="center").pack(pady=(0, 20)) 
        
        description = ("This intelligent assistant provides you with a quick and simple way to estimate your personal "
                       "carbon footprint (daily and monthly) based on three key consumption areas. ")
        ctk.CTkLabel(self.splash_frame, text=description, wraplength=450, 
                     font=ctk.CTkFont(size=14), justify="center", text_color="gray70").pack(pady=20, padx=50)

        ctk.CTkButton(self.splash_frame, text="START CALCULATION", 
                      command=self.show_main_interface, 
                      fg_color=PRIMARY_COLOR, hover_color="#16A085",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      width=200, height=50, corner_radius=10).pack(pady=50)

    def show_main_interface(self):
        self.splash_frame.destroy()
        self.build_main_ui()

    # --- Main UI Build (Unchanged in structure) ---
    def build_main_ui(self):
        
        input_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=FRAME_COLOR, border_color=PRIMARY_COLOR, border_width=2)
        input_frame.pack(pady=20, padx=30, fill="x")

        ctk.CTkLabel(input_frame, text="Enter Your Daily Consumption", 
                     font=ctk.CTkFont(size=18, weight="bold"), text_color=PRIMARY_COLOR).grid(row=0, column=0, columnspan=3, pady=(10, 20))

        # --- Setup GRID Configuration ---
        input_frame.grid_columnconfigure(0, weight=0, minsize=180) 
        input_frame.grid_columnconfigure(1, weight=1)              
        input_frame.grid_columnconfigure(2, weight=0, minsize=170) 
        
        # 1. Transport Section 
        self.transport_display_label = ctk.CTkLabel(input_frame, text="Transport CO2: 0.00 kg (Click Input)", anchor='w', text_color="#F39C12")
        self.create_transport_field(input_frame, row=1)
        
        # 2. Energy Section 
        self.energy_display_label = ctk.CTkLabel(input_frame, text="Energy (kWh): 0.00 kWh", anchor='w', text_color="#F39C12")
        self.create_energy_option_field(input_frame, row=2)
        
        # 3. Food Section 
        self.create_food_field(input_frame, row=4)


        # Calculation Button 
        ctk.CTkButton(input_frame, text="CALCULATE FOOTPRINT 🧮", 
                      command=self.calculate_and_display, 
                      fg_color=PRIMARY_COLOR, hover_color="#16A085",
                      font=ctk.CTkFont(size=15, weight="bold"),
                      corner_radius=8).grid(row=5, column=0, columnspan=3, pady=20, padx=20)
        
        # --- Results and Recommendation Frames ---
        
        results_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=FRAME_COLOR)
        results_frame.pack(pady=10, padx=30, fill="x")
        self.daily_co2_label = self.create_result_label(results_frame, "📊 Daily Footprint:", "0.00 kg CO2", ACCENT_COLOR)
        self.monthly_co2_label = self.create_result_label(results_frame, "📈 Monthly Footprint:", "0.00 kg CO2", "#F39C12")
        
        offset_frame = ctk.CTkFrame(self, corner_radius=10, fg_color=FRAME_COLOR)
        offset_frame.pack(pady=10, padx=30, fill="x")
        ctk.CTkLabel(offset_frame, text="🌳 Carbon Offset & Tree Estimation", 
                     font=ctk.CTkFont(size=16, weight="bold"), text_color=PRIMARY_COLOR).pack(pady=(10, 10))
        
        self.offset_co2_label = self.create_result_label(offset_frame, "Required Annual Offset:", "0.00 kg CO2", "#2ECC71")
        self.tax_cost_label = self.create_result_label(offset_frame, "💰 Est. Annual Carbon Tax:", "0.00 EGP", "#E74C3C") 
        self.trees_label = self.create_result_label(offset_frame, "Trees Needed (Annual):", "0 trees", "#27AE60")
        
        self.recommendation_frame = self.create_recommendation_section()
        self.recommendation_frame.pack_forget()

    # --- UI Helpers (Transport, Energy, Food) ---
    # (Methods for creating fields and toplevels are kept as they were)

    def create_transport_field(self, parent_frame, row):
        ctk.CTkLabel(parent_frame, text="1. Transport (km/Mode):", anchor='w').grid(row=row, column=0, sticky="w", padx=15, pady=10)
        self.transport_display_label.grid(row=row, column=1, sticky="w", padx=10, pady=10)
        ctk.CTkButton(parent_frame, text="Input Transport Details 🚗", 
                      command=self.open_transport_calculator, 
                      fg_color="#F39C12", hover_color="#C09A32", width=150).grid(row=row, column=2, sticky="e", padx=15, pady=10)


    def create_energy_option_field(self, parent_frame, row):
        ctk.CTkLabel(parent_frame, text="2. Energy (kWh/Method):", anchor='w').grid(row=row, column=0, sticky="w", padx=15, pady=5)
        options_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        options_frame.grid(row=row, column=1, columnspan=2, sticky="w", padx=10, pady=5) 

        self.energy_choice = ctk.IntVar(value=1) 
        ctk.CTkRadioButton(options_frame, text="Direct Value", variable=self.energy_choice, value=1, command=self.toggle_energy_input).pack(side="left", padx=10)
        ctk.CTkRadioButton(options_frame, text="Estimate Devices", variable=self.energy_choice, value=2, command=self.toggle_energy_input).pack(side="left", padx=10)

        ctk.CTkLabel(parent_frame, text="", fg_color="transparent").grid(row=row + 1, column=0, sticky="ew", padx=15, pady=5) 
        self.energy_display_label.grid(row=row + 1, column=1, sticky="w", padx=10)
        
        self.direct_entry = ctk.CTkEntry(parent_frame, textvariable=self.energy_direct_var, 
                                        placeholder_text="Enter kWh directly...", width=150)
        self.direct_entry.grid(row=row + 1, column=2, sticky="e", padx=15)
        
        self.estimate_button = ctk.CTkButton(parent_frame, text="Start Estimation", command=self.open_energy_estimator, 
                                            width=150, fg_color="#F39C12", hover_color="#C09A32")
        self.estimate_button.grid_forget() 

    def create_food_field(self, parent_frame, row):
        ctk.CTkLabel(parent_frame, text="3. Food (Portions/Meals):", anchor='w').grid(row=row, column=0, sticky="w", padx=15, pady=10)
        ctk.CTkLabel(parent_frame, text="", fg_color="transparent").grid(row=row, column=1, sticky="ew")
        ctk.CTkEntry(parent_frame, textvariable=self.food_var, 
                     placeholder_text="Numeric value...", width=150, fg_color="gray25").grid(row=row, column=2, sticky="e", padx=15, pady=10)

    def toggle_energy_input(self):
        choice = self.energy_choice.get()
        row, column = 3, 2

        self.direct_entry.grid_forget()
        self.estimate_button.grid_forget()
        self.energy_val.set(0.0) 
        
        if choice == 1:
            self.direct_entry.grid(row=row, column=column, sticky="e", padx=15)
            try:
                kwh = float(self.energy_direct_var.get())
                self.energy_display_label.configure(text=f"Energy (kWh): {kwh:.2f} kWh (Direct)", text_color=PRIMARY_COLOR)
            except:
                self.energy_display_label.configure(text=f"Energy (kWh): 0.00 kWh (Direct)", text_color=PRIMARY_COLOR)
        else: 
            self.estimate_button.grid(row=row, column=column, sticky="e", padx=15)
            self.energy_display_label.configure(text=f"Energy (kWh): 0.00 kWh (Est.)", text_color="#F39C12")

    # --- Transport & Energy Toplevels (Omitted for brevity - assumed unchanged) ---
    def open_transport_calculator(self):
        self.TransportCalculator(self)
    class TransportCalculator(ctk.CTkToplevel):
        def __init__(self, master):
            super().__init__(master)
            self.master = master
            self.title("Transport Details")
            self.geometry("400x300")
            self.transient(master)
            self.grab_set()

            self.mode_var = ctk.StringVar(value="Car")
            self.distance_var = ctk.StringVar(value="") 

            ctk.CTkLabel(self, text="Calculate Transport CO2 (kg)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

            mode_frame = ctk.CTkFrame(self, fg_color="transparent")
            mode_frame.pack(pady=5, padx=20, fill="x")
            ctk.CTkLabel(mode_frame, text="Select Mode:").pack(side="left", padx=10)
            
            modes = list(EMISSION_FACTORS.keys())
            mode_options = [m for m in modes if m not in ["Energy_Factor", "Food"]]
            ctk.CTkOptionMenu(mode_frame, variable=self.mode_var, values=mode_options).pack(side="right", fill="x", expand=True)

            distance_frame = ctk.CTkFrame(self, fg_color="transparent")
            distance_frame.pack(pady=5, padx=20, fill="x")
            ctk.CTkLabel(distance_frame, text="Distance (km):").pack(side="left", padx=10)
            self.distance_entry = ctk.CTkEntry(distance_frame, textvariable=self.distance_var)
            self.distance_entry.pack(side="right", fill="x", expand=True)

            ctk.CTkButton(self, text="Apply Transport CO2", command=self.apply_calculation, 
                          fg_color=PRIMARY_COLOR, hover_color="#16A085").pack(pady=20)

        def apply_calculation(self):
            try:
                if not self.distance_var.get().strip():
                    raise ValueError("Error: Please enter the distance (km).")

                mode = self.mode_var.get()
                distance = float(self.distance_var.get())
                
                if distance < 0: raise ValueError("Distance must be positive.")

                factor = EMISSION_FACTORS.get(mode, 0.2)
                calculated_co2 = distance * factor
                
                self.master.transport_co2.set(calculated_co2)
                self.master.transport_display_label.configure(text=f"Transport CO2: {calculated_co2:.2f} kg ({mode})", text_color=PRIMARY_COLOR)
                
                self.destroy()
            except ValueError as e:
                messagebox.showerror("Input Error ❌", str(e))
            except Exception as e:
                messagebox.showerror("System Error", f"An unexpected error occurred: {e}")
                
    def open_energy_estimator(self):
        self.EnergyEstimator(self)

    class EnergyEstimator(ctk.CTkToplevel):
        def __init__(self, master):
            super().__init__(master)
            self.master = master
            self.title("Energy Estimation")
            self.geometry("400x450")
            self.transient(master)
            self.grab_set()

            ctk.CTkLabel(self, text="Estimate Daily Energy (kWh)", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)
            
            self.tablet_var = ctk.StringVar(value="") 
            self.large_var = ctk.StringVar(value="")
            self.bulb_var = ctk.StringVar(value="")
            self.small_var = ctk.StringVar(value="")
            
            self.entry_vars = {
                "Tablet/Small Devices (Units):": self.tablet_var,
                "Large Appliances (Units):": self.large_var,
                "Lighting Bulbs (Units):": self.bulb_var,
                "Other Small Devices (Units):": self.small_var,
            }
            
            for label, var in self.entry_vars.items():
                self.create_estimator_input(label, var)
            
            ctk.CTkButton(self, text="Apply Estimated kWh", command=self.apply_estimation, 
                          fg_color=PRIMARY_COLOR, hover_color="#16A085").pack(pady=20)
            
        def create_estimator_input(self, label_text, var):
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(pady=5, padx=20, fill="x")
            ctk.CTkLabel(frame, text=label_text).pack(side="left", padx=10)
            ctk.CTkEntry(frame, textvariable=var).pack(side="right", fill="x", expand=True)

        def apply_estimation(self):
            try:
                counts = {}
                for label, var in self.entry_vars.items():
                    value = var.get().strip()
                    if not value:
                        raise ValueError(f"Error: Please enter a count for all fields, especially '{label.split('(')[0].strip()}'.")
                    
                    count = int(value)
                    if count < 0:
                        raise ValueError("Counts must be zero or positive.")
                    
                    if "Tablet" in label: key = "Tablet_Devices"
                    elif "Large" in label: key = "Large_Appliances"
                    elif "Bulbs" in label: key = "Lighting_Bulbs"
                    elif "Other Small" in label: key = "Small_Devices"
                    else: continue
                    counts[key] = count
                
                estimated_kwh = (
                    counts["Tablet_Devices"] * ENERGY_ESTIMATION["Tablet_Devices"] +
                    counts["Large_Appliances"] * ENERGY_ESTIMATION["Large_Appliances"] +
                    counts["Lighting_Bulbs"] * ENERGY_ESTIMATION["Lighting_Bulbs"] * ENERGY_ESTIMATION["Average_Usage_Hours"] +
                    counts["Small_Devices"] * ENERGY_ESTIMATION["Small_Devices"]
                )
                
                self.master.energy_val.set(estimated_kwh)
                self.master.energy_display_label.configure(text=f"Energy (kWh): {estimated_kwh:.2f} kWh (Est.)", text_color=PRIMARY_COLOR)
                
                self.destroy()
            except ValueError as e:
                messagebox.showerror("Input Error ❌", str(e))
            except Exception as e:
                messagebox.showerror("System Error", f"An unexpected error occurred: {e}")
                
    # --- Calculation Logic (Unchanged) ---
    def calculate_and_display(self):
        
        try:
            # ... (Validation unchanged) ...
            transport_co2 = self.transport_co2.get()
            if transport_co2 == 0.0 and self.transport_display_label.cget("text") == "Transport CO2: 0.00 kg (Click Input)":
                 messagebox.showwarning("Missing Data", "Please input transport details first.")
                 return
            
            energy_kwh = 0.0
            if self.energy_choice.get() == 1:
                direct_value = self.energy_direct_var.get().strip()
                if not direct_value:
                    raise ValueError("Error: Please enter the Direct Energy value (kWh).")
                
                energy_kwh = float(direct_value)
                self.energy_val.set(energy_kwh)
                self.energy_display_label.configure(text=f"Energy (kWh): {energy_kwh:.2f} kWh (Direct)", text_color=PRIMARY_COLOR)
            else:
                energy_kwh = self.energy_val.get()
                if energy_kwh == 0.0:
                     messagebox.showwarning("Missing Data", "Please input estimated device counts using 'Start Estimation'.")
                     return

            if energy_kwh < 0: raise ValueError("Energy value must be positive.")
            
            food_input = self.food_var.get().strip()
            if not food_input:
                raise ValueError("Error: Please enter the Food portions/meals.")
                
            food_portions = float(food_input)
            if food_portions < 0: raise ValueError("Food portions must be positive.")

            # Final Daily CO2 Calculation
            daily_co2 = (
                transport_co2 + 
                (energy_kwh * EMISSION_FACTORS["Energy_Factor"]) +
                (food_portions * EMISSION_FACTORS["Food"])
            )
            
            # 4. Update UI and Recommendation
            self.daily_co2 = daily_co2 
            self.update_recommendation() 

            monthly_co2 = daily_co2 * DAYS_IN_MONTH
            annual_co2 = daily_co2 * 365.25 
            
            # CALCULATION: Carbon Tax Cost in EGP
            annual_tax_cost = annual_co2 * CARBON_TAX_PER_KG

            trees_needed = annual_co2 / CO2_PER_TREE_PER_YEAR
            
            self.daily_co2_label.configure(text=f"{daily_co2:.2f} kg CO2")
            self.monthly_co2_label.configure(text=f"{monthly_co2:.2f} kg CO2")
            self.offset_co2_label.configure(text=f"{annual_co2:.2f} kg CO2")
            self.tax_cost_label.configure(text=f"{annual_tax_cost:.2f} EGP") 
            self.trees_label.configure(text=f"{trees_needed:.1f} trees")
            
            messagebox.showinfo("Success ✅", "Results updated successfully!")

        except ValueError as e:
            messagebox.showerror("Input Error ❌", str(e))
            self.recommendation_frame.pack_forget()
        except Exception as e:
            messagebox.showerror("System Error", f"An unexpected error occurred: {e}")

    # --- Footer Helpers (Unchanged in structure) ---
    def create_result_label(self, parent_frame, label_text, initial_value, color):
        frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        frame.pack(fill='x', padx=20, pady=8)
        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=14, weight="bold")).pack(side='left', anchor='w')
        result_label = ctk.CTkLabel(frame, text=initial_value, font=ctk.CTkFont(size=16, weight="bold"), text_color=color)
        result_label.pack(side='right', anchor='e')
        return result_label
        
    def create_recommendation_section(self):
        recommendation_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="gray17")
        ctk.CTkLabel(recommendation_frame, text="✅ Personalized Recommendations:", 
                     font=ctk.CTkFont(size=16, weight="bold"), text_color="#A9CCE3").pack(pady=(10, 5))
        self.recommendation_textbox = ctk.CTkTextbox(recommendation_frame, height=50, corner_radius=8, 
                       wrap="word", fg_color="gray25", activate_scrollbars=False)
        self.recommendation_textbox.insert("end", "Please enter consumption values first.")
        self.recommendation_textbox.pack(fill='x', padx=15, pady=10)
        self.recommendation_textbox.configure(state="disabled")
        return recommendation_frame
        
    # --- Brief and Organized Recommendation Logic in English ---
    def update_recommendation(self):
        co2 = self.daily_co2
        
        if co2 <= 5.0:
            rec_text = "🟢 **Planetary Champion (Very Low):** Maintain excellent habits. Consider supporting carbon offset projects."
        elif 5.0 < co2 <= 15.0:
            rec_text = "🟡 **Good (Average):** Your footprint is manageable. Focus on using predictive models to optimize energy consumption."
        elif 15.0 < co2 <= 30.0:
            rec_text = "🟠 **High:** Significant opportunity for savings. Use clustering algorithms to identify your highest emission activity and reduce it."
        else:
            rec_text = "🔴 **Critical (Very High):** Immediate action required! Adopt AI-powered coaching to achieve a 25% emissions reduction."
            
        self.recommendation_textbox.configure(state="normal")
        self.recommendation_textbox.delete("1.0", "end")
        self.recommendation_textbox.insert("end", rec_text)
        self.recommendation_textbox.configure(state="disabled")
        
        self.recommendation_frame.pack(pady=20, padx=30, fill="x")


# --------------------------------------------------------
# 6. Entry Point
# --------------------------------------------------------

if __name__ == "__main__":
    app = SimplifiedCarbonApp()
    app.mainloop()