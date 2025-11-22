import os
import tkinter as tk
from tkinter import filedialog, messagebox

from utilities import config
import layoutObfuscation
import dataflowObfuscation
import controlflowObfuscation
import deadcodeObfuscation

class ObfuscationApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Solidity Obfuscator")

        # state
        self.input_path_var = tk.StringVar()
        self.output_name_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()

        self.controlflow_var = tk.BooleanVar(value=True)
        self.dataflow_var = tk.BooleanVar(value=False)
        self.layout_var = tk.BooleanVar(value=False)
        self.deadcode_var = tk.BooleanVar(value=False)

        # configuraion
        self.config_dict = dict()

        # configuration -> control flow configuration
        self.controlflow_config_instruction_insert_var = tk.BooleanVar(value=True)
        self.controlflow_config_instruction_replace_var = tk.BooleanVar(value=True)
        self.controlflow_config_insert_opaque_predicate_var = tk.BooleanVar(value=True)
        self.controlflow_config_shuffle_code_block_var = tk.BooleanVar(value=True)

        # UI
        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.grid(row=0, column=0, sticky="nsew")

        # 1. INPUT
        btn_select = tk.Button(
            frame,
            text="Select Solidity File",
            command=self.select_input_file,
            width=20,
        )
        btn_select.grid(row=0, column=0, padx=(0, 8), pady=(0, 8), sticky="w")

        lbl_input = tk.Label(frame, text="Input file:")
        lbl_input.grid(row=1, column=0, sticky="w")

        entry_input = tk.Entry(
            frame,
            textvariable=self.input_path_var,
            width=60,
            state="readonly",
        )
        entry_input.grid(row=1, column=1, padx=(8, 0), pady=(0, 8), sticky="w")

        # 2. OUTPUT NAME
        lbl_output_name = tk.Label(frame, text="Output file name:")
        lbl_output_name.grid(row=2, column=0, sticky="w")

        entry_output = tk.Entry(
            frame,
            textvariable=self.output_name_var,
            width=40,
        )
        entry_output.grid(row=2, column=1, padx=(8, 0), pady=(0, 4), sticky="w")

        hint_label = tk.Label(
            frame,
            text="(Default: original file name + '_obfu')",
            fg="gray",
        )
        hint_label.grid(row=3, column=1, sticky="w")

        # 3. OUTPUT LOCATION
        btn_select_outdir = tk.Button(
            frame,
            text="Select Output Folder",
            command=self.select_output_folder,
            width=20,
        )
        btn_select_outdir.grid(row=4, column=0, padx=(0, 8), pady=(10, 4), sticky="w")

        lbl_output_dir = tk.Label(frame, text="Output folder:")
        lbl_output_dir.grid(row=5, column=0, sticky="w")

        entry_output_dir = tk.Entry(
            frame,
            textvariable=self.output_dir_var,
            width=60,
            state="readonly",
        )
        entry_output_dir.grid(row=5, column=1, padx=(8, 0), pady=(0, 8), sticky="w")

        # 4. Obfuscation type
        lbl_obf = tk.Label(frame, text="Obfuscation types:")
        lbl_obf.grid(row=6, column=0, pady=(10, 0), sticky="nw")

        types_frame = tk.Frame(frame)
        types_frame.grid(row=6, column=1, pady=(10, 0), sticky="w")

        chk_controlflow = tk.Checkbutton(
            types_frame,
            text="Control Flow Obfuscation",
            variable=self.controlflow_var,
        )
        chk_controlflow.grid(row=0, column=0, sticky="w")

        chk_dataflow = tk.Checkbutton(
            types_frame,
            text="Data Flow Obfuscation",
            variable=self.dataflow_var,
        )
        chk_dataflow.grid(row=1, column=0, sticky="w")

        chk_layout = tk.Checkbutton(
            types_frame,
            text="Layout Obfuscation",
            variable=self.layout_var,
        )
        chk_layout.grid(row=2, column=0, sticky="w")

        chk_deadcode = tk.Checkbutton(
            types_frame,
            text="Dead Code Obfuscation",
            variable=self.deadcode_var,
        )
        chk_deadcode.grid(row=3, column=0, sticky="w")

        btn_edit_config = tk.Button(
            frame,
            text="Edit Configuration",
            command=self.open_config_window,
            width=20,
        )
        btn_edit_config.grid(row=7, column=0, padx=(0, 8), pady=(0, 8), sticky="w")

        # 5. Start 
        btn_start = tk.Button(
            frame,
            text="Start Obfuscation",
            command=self.start_obfuscation,
            width=20,
        )
        btn_start.grid(row=8, column=0, columnspan=2, pady=(15, 0))

    # configuration
    def apply_config(self):
        # file config
        self.input_path_var.set(self.config_dict["inputPath"])
        self.output_name_var.set(self.config_dict["outputName"])
        self.output_dir_var.set(self.config_dict["outputDir"])
        # obfuscation type config
        self.controlflow_var.set(self.config_dict["obfuscationType"][0]["controlflow"])
        self.dataflow_var.set(self.config_dict["obfuscationType"][1]["dataflow"])
        self.layout_var.set(self.config_dict["obfuscationType"][2]["layout"])
        self.deadcode_var.set(self.config_dict["obfuscationType"][3]["deadcode"])
        # control flow config
        self.controlflow_config_instruction_insert_var.set(self.config_dict["controlflowConfig"][0]["instructionInsert"])
        self.controlflow_config_instruction_replace_var.set(self.config_dict["controlflowConfig"][1]["instructionReplace"])
        self.controlflow_config_insert_opaque_predicate_var.set(self.config_dict["controlflowConfig"][2]["insertOpaquePredicate"])
        self.controlflow_config_shuffle_code_block_var.set(self.config_dict["controlflowConfig"][3]["shuffleCodeBlock"])

    def get_config(self) -> dict:
        # file config
        self.config_dict["inputPath"] = self.input_path_var.get()
        self.config_dict["outputName"] = self.output_name_var.get()
        self.config_dict["outputDir"] = self.output_dir_var.get()
        # obfuscation type config
        self.config_dict["obfuscationType"][0]["controlflow"] = self.controlflow_var.get()
        self.config_dict["obfuscationType"][1]["dataflow"] = self.dataflow_var.get()
        self.config_dict["obfuscationType"][2]["layout"] = self.layout_var.get()
        self.config_dict["obfuscationType"][3]["deadcode"] = self.deadcode_var.get()
        # control flow config
        self.config_dict["controlflowConfig"][0]["instructionInsert"] = self.controlflow_config_instruction_insert_var.get()
        self.config_dict["controlflowConfig"][1]["instructionReplace"] = self.controlflow_config_instruction_replace_var.get()
        self.config_dict["controlflowConfig"][2]["insertOpaquePredicate"] = self.controlflow_config_insert_opaque_predicate_var.get()
        self.config_dict["controlflowConfig"][3]["shuffleCodeBlock"] = self.controlflow_config_shuffle_code_block_var.get()

    # configuration
    def open_config_window(self):
        config_window = tk.Toplevel(self.root)  # Link to the main window
        config_window.title("Configuration Window")
        config_window.geometry("300x200")  # Set dimensions

        lbl_control_flow = tk.Label(config_window, text="Control flow configurations:")
        lbl_control_flow.grid(row=0, column=0, pady=(10, 0), sticky="nw")

        control_flow_frame = tk.Frame(config_window)
        control_flow_frame.grid(row=1, column=0, pady=(10, 0), sticky="w")

        chk_controlflow_instuction_insert = tk.Checkbutton(
            control_flow_frame,
            text="instruction insert",
            variable=self.controlflow_config_instruction_insert_var,
        )
        chk_controlflow_instuction_insert.grid(row=0, column=0, sticky="w")

        chk_controlflow_instruction_replace = tk.Checkbutton(
            control_flow_frame,
            text="instruction replace",
            variable=self.controlflow_config_instruction_replace_var,
        )
        chk_controlflow_instruction_replace.grid(row=1, column=0, sticky="w")

        chk_controlflow_insert_opaque_predicate = tk.Checkbutton(
            control_flow_frame,
            text="insert opaque predicate",
            variable=self.controlflow_config_insert_opaque_predicate_var,
        )
        chk_controlflow_insert_opaque_predicate.grid(row=2, column=0, sticky="w")

        chk_controlflow_shuffle_code_block = tk.Checkbutton(
            control_flow_frame,
            text="shuffle code block",
            variable=self.controlflow_config_shuffle_code_block_var,
        )
        chk_controlflow_shuffle_code_block.grid(row=3, column=0, sticky="w")

    # handleling

    def select_input_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Solidity file",
            filetypes=[("Solidity files", "*.sol"), ("All files", "*.*")],
        )
        if not filepath:
            return

        self.input_path_var.set(filepath)

        base_dir = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)

        # defualt output name and location
        default_out_name = f"{name}_obfu{ext}"
        self.output_name_var.set(default_out_name)
        self.output_dir_var.set(base_dir)

    def select_output_folder(self):
        folder = filedialog.askdirectory(
            title="Select Output Folder"
        )
        if not folder:
            return
        self.output_dir_var.set(folder)

    def start_obfuscation(self):
        input_path = self.input_path_var.get().strip()
        output_name = self.output_name_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            output_dir = os.path.dirname(input_path)
            self.output_dir_var.set(output_dir)

        if not input_path:
            messagebox.showerror("Error", "Please select an input Solidity file first.")
            return

        if not os.path.exists(input_path):
            messagebox.showerror("Error", f"Input file does not exist:\n{input_path}")
            return

        if not output_name:
            messagebox.showerror("Error", "Please enter an output file name.")
            return

        # check at least 1 item selected on check box
        if not (
            self.controlflow_var.get()
            or self.dataflow_var.get()
            or self.layout_var.get()
            or self.deadcode_var.get()
        ):
            messagebox.showerror(
                "Error",
                "Please select at least one obfuscation type."
            )
            return


        output_path = os.path.join(output_dir, output_name)

        try:
            with open(input_path, "r", encoding="utf-8") as f:
                sol_content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read input file:\n{e}")
            return

        try:
            # Layout
            if self.layout_var.get():
                lo = layoutObfuscation.layoutObfuscation(sol_content)
                sol_content = lo.run()

            # Data flow
            if self.dataflow_var.get():
                dfo = dataflowObfuscation.dataflowObfuscation(sol_content)
                sol_content = dfo.obfuscate()

            # Control flow
            if self.controlflow_var.get():
                cfoCfg = controlflowObfuscation.controlflowConfig(
                    self.controlflow_config_instruction_insert_var.get(),
                    self.controlflow_config_instruction_replace_var.get(),
                    self.controlflow_config_insert_opaque_predicate_var.get(),
                    self.controlflow_config_shuffle_code_block_var.get())
                cfo = controlflowObfuscation.controlflowObfuscation(sol_content)
                sol_content = cfo.run(cfoCfg)

            # Dead code（目前只是 placeholder）
            if self.deadcode_var.get():
                dco = deadcodeObfuscation.deadcodeObfuscation(sol_content)
                sol_content = dco.run()
                pass

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(sol_content)

            messagebox.showinfo(
                "Success",
                f"Obfuscation completed.\nOutput saved to:\n{output_path}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"Obfuscation failed:\n{e}")


def main():
    root = tk.Tk()
    app = ObfuscationApp(root)
    # load configuration
    configObject = config.config(".\\Configuration.json")
    app.config_dict = configObject.load_config()
    app.apply_config()

    # main loop
    root.mainloop()

    # save configuration
    app.get_config()
    configObject.save_config(app.config_dict)


if __name__ == "__main__":
    main()
