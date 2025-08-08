import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
from dotenv import load_dotenv
import os
import io
import requests
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

class ImageAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Azure AI Vision Image Analyzer")
        self.root.geometry("1400x900")
        
        # Load environment variables
        load_dotenv()
        self.ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
        self.ai_key = os.getenv('AI_SERVICE_KEY')
        
        # Initialize Azure client
        try:
            self.cv_client = ImageAnalysisClient(
                endpoint=self.ai_endpoint,
                credential=AzureKeyCredential(self.ai_key))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize Azure client: {str(e)}")
            self.root.destroy()
            return
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Frame for controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Create notebook for input methods
        input_notebook = ttk.Notebook(control_frame)
        input_notebook.pack(fill=tk.X, pady=5)
        
        # File input tab
        file_tab = ttk.Frame(input_notebook)
        input_notebook.add(file_tab, text="File Input")
        
        ttk.Label(file_tab, text="Image File:").grid(row=0, column=0, sticky=tk.W)
        self.file_entry = ttk.Entry(file_tab, width=50)
        self.file_entry.grid(row=0, column=1, sticky=tk.EW)
        ttk.Button(file_tab, text="Browse...", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # URL input tab
        url_tab = ttk.Frame(input_notebook)
        input_notebook.add(url_tab, text="URL Input")
        
        ttk.Label(url_tab, text="Image URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_entry = ttk.Entry(url_tab, width=50)
        self.url_entry.grid(row=0, column=1, sticky=tk.EW)
        ttk.Button(url_tab, text="Load URL", command=self.load_url).grid(row=0, column=2, padx=5)
        
        # Analyze button
        ttk.Button(control_frame, text="Analyze Image", command=self.analyze_image).pack(pady=10)
        
        # Main content area
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Results display
        self.results_text = tk.Text(main_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image display frame
        image_frame = ttk.Frame(main_frame, width=600)
        image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # Create notebook for multiple image tabs
        self.notebook = ttk.Notebook(image_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab for original image
        original_tab = ttk.Frame(self.notebook)
        self.notebook.add(original_tab, text="Original Image")
        self.original_img_label = ttk.Label(original_tab)
        self.original_img_label.pack(fill=tk.BOTH, expand=True)
        
        # Tab for object annotations
        objects_tab = ttk.Frame(self.notebook)
        self.notebook.add(objects_tab, text="Object Detection")
        self.objects_img_label = ttk.Label(objects_tab)
        self.objects_img_label.pack(fill=tk.BOTH, expand=True)
        
        # Tab for people annotations
        people_tab = ttk.Frame(self.notebook)
        self.notebook.add(people_tab, text="People Detection")
        self.people_img_label = ttk.Label(people_tab)
        self.people_img_label.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        file_tab.columnconfigure(1, weight=1)
        url_tab.columnconfigure(1, weight=1)
    
    def browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp"), ("All files", "*.*")]
        )
        if filepath:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filepath)
            self.display_image(filepath, self.original_img_label)
            # Clear any URL image data when browsing files
            if hasattr(self, 'url_image_data'):
                del self.url_image_data
    
    def load_url(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showwarning("Warning", "Please enter an image URL")
            return
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Load image from URL
            self.url_image_data = response.content
            image = Image.open(io.BytesIO(self.url_image_data))
            
            # Display the image
            photo = ImageTk.PhotoImage(image)
            self.original_img_label.configure(image=photo)
            self.original_img_label.image = photo  # Keep a reference
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image from URL: {str(e)}")
    
    def display_image(self, filepath, label_widget):
        try:
            image = Image.open(filepath)
            photo = ImageTk.PhotoImage(image)
            label_widget.configure(image=photo)
            label_widget.image = photo  # Keep a reference
            return image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")
            return None
    
    def analyze_image(self):
        # Check which input method is being used
        if hasattr(self, 'url_image_data'):
            # Analyze from URL (using the downloaded image data)
            self.analyze_from_url_data()
        elif self.file_entry.get():
            # Analyze from file
            self.analyze_from_file()
        else:
            messagebox.showwarning("Warning", "Please select an image file or enter an image URL first")
    
    def analyze_from_file(self):
        image_file = self.file_entry.get()
        try:
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Analyzing {image_file}...\n\n")
            self.results_text.update()
            
            # Read image data
            with open(image_file, "rb") as f:
                image_data = f.read()
            
            # Analyze image
            result = self.cv_client.analyze(
                image_data=image_data,
                visual_features=[
                    VisualFeatures.CAPTION,
                    VisualFeatures.DENSE_CAPTIONS,
                    VisualFeatures.TAGS,
                    VisualFeatures.OBJECTS,
                    VisualFeatures.PEOPLE],
            )
            
            # Display results and annotations
            self.display_results(image_file, result, is_url=False)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
        finally:
            self.results_text.config(state=tk.DISABLED)
    
    def analyze_from_url_data(self):
        try:
            url = self.url_entry.get()
            self.results_text.config(state=tk.NORMAL)
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Analyzing image from URL: {url}...\n\n")
            self.results_text.update()
            
            # Analyze the downloaded image data
            result = self.cv_client.analyze(
                image_data=self.url_image_data,  # Use the downloaded image data
                visual_features=[
                    VisualFeatures.CAPTION,
                    VisualFeatures.DENSE_CAPTIONS,
                    VisualFeatures.TAGS,
                    VisualFeatures.OBJECTS,
                    VisualFeatures.PEOPLE],
            )
            
            # Display results and annotations
            self.display_results(url, result, is_url=True)
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
        finally:
            self.results_text.config(state=tk.DISABLED)
    
    def display_results(self, source, result, is_url=False):
        # Display captions
        if result.caption is not None:
            self.results_text.insert(tk.END, "=== MAIN CAPTION ===\n")
            self.results_text.insert(tk.END, f"'{result.caption.text}' (confidence: {result.caption.confidence * 100:.2f}%)\n\n")
        
        if result.dense_captions is not None:
            self.results_text.insert(tk.END, "=== DENSE CAPTIONS ===\n")
            for caption in result.dense_captions.list:
                self.results_text.insert(tk.END, f"'{caption.text}' (confidence: {caption.confidence * 100:.2f}%)\n")
            self.results_text.insert(tk.END, "\n")
        
        # Display tags
        if result.tags is not None:
            self.results_text.insert(tk.END, "=== TAGS ===\n")
            for tag in result.tags.list:
                self.results_text.insert(tk.END, f"'{tag.name}' (confidence: {tag.confidence * 100:.2f}%)\n")
            self.results_text.insert(tk.END, "\n")
        
        # Process objects and people
        try:
            if is_url:
                # For URL source, use the image we already downloaded
                image = Image.open(io.BytesIO(self.url_image_data))
            else:
                # For file source, open the file
                image = Image.open(source)
            
            if result.objects is not None:
                self.results_text.insert(tk.END, "=== DETECTED OBJECTS ===\n")
                for detected_object in result.objects.list:
                    self.results_text.insert(tk.END, f"- '{detected_object.tags[0].name}' (confidence: {detected_object.tags[0].confidence * 100:.2f}%)\n")
                
                # Create and display object annotations
                objects_image = self.annotate_objects(image.copy(), result.objects.list)
                self.display_annotated_image(objects_image, self.objects_img_label)
                
                self.results_text.insert(tk.END, "\n")
            
            if result.people is not None:
                self.results_text.insert(tk.END, "=== DETECTED PEOPLE ===\n")
                for detected_person in result.people.list:
                    confidence = detected_person.confidence * 100
                    if confidence > 20:  # Only show if confidence > 20%
                        self.results_text.insert(tk.END, f"- Person detected (confidence: {confidence:.2f}%)\n")
                
                # Create and display people annotations
                people_image = self.annotate_people(image.copy(), result.people.list)
                self.display_annotated_image(people_image, self.people_img_label)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image for annotations: {str(e)}")
    
    def annotate_objects(self, image, detected_objects):
        try:
            draw = ImageDraw.Draw(image)
            color = 'cyan'
            
            for detected_object in detected_objects:
                # Draw object bounding box
                r = detected_object.bounding_box
                bounding_box = ((r.x, r.y), (r.x + r.width, r.y + r.height)) 
                draw.rectangle(bounding_box, outline=color, width=3)
                
                # Draw label
                draw.text((r.x, r.y), detected_object.tags[0].name, fill=color)
            
            return image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to annotate objects: {str(e)}")
            return None
    
    def annotate_people(self, image, detected_people):
        try:
            draw = ImageDraw.Draw(image)
            color = 'yellow'  # Different color for people annotations
            
            for detected_person in detected_people:
                if detected_person.confidence > 0.2:
                    r = detected_person.bounding_box
                    bounding_box = ((r.x, r.y), (r.x + r.width, r.y + r.height)) 
                    draw.rectangle(bounding_box, outline=color, width=3)
                    draw.text((r.x, r.y), "Person", fill=color)
            
            return image
        except Exception as e:
            messagebox.showerror("Error", f"Failed to annotate people: {str(e)}")
            return None
    
    def display_annotated_image(self, image, label_widget):
        if image is None:
            return
            
        try:
            # Resize image to fit in the display area if needed
            max_size = 600
            width, height = image.size
            if width > max_size or height > max_size:
                ratio = min(max_size/width, max_size/height)
                image = image.resize((int(width*ratio), int(height*ratio)), Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            label_widget.configure(image=photo)
            label_widget.image = photo  # Keep a reference
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display annotated image: {str(e)}")

def main():
    root = tk.Tk()
    app = ImageAnalysisApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()