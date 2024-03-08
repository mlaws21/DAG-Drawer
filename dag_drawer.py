import tkinter as tk
import tkinter.simpledialog
from tkinter import messagebox
import math
import random


class Dag_Drawer:
    def __init__(self, in_nodes=[], in_edges=[], size=2000):
        root = tk.Tk()
        root.title("DAG Drawer")
        root.bind("<Command-z>", self.undo)
        root.bind("t", self.toggle)
        root.bind("p", self.dump)


        root.bind("<Escape>", self.clear_edge)
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        size = min(size, screen_width, screen_height)
        self.size = size
        self.canvas = tk.Canvas(root, width=size, height=size, bg='black')
        self.canvas.pack()
        
        
        self.canvas.bind("<Button-1>", self.handle_click)
        self.not_active = "Edges"
        button_font = ('Arial', 16, 'bold')
        self.button = tk.Button(self.canvas, text=f"Switch to Adding {self.not_active}", command=self.toggle, highlightbackground='black', font=button_font,
                          padx=10, pady=10)
        button_window = self.canvas.create_window(size - size / 20, size / 20, anchor=tk.NE, window=self.button)
        
        print_button = tk.Button(self.canvas, text="Print Nodes and Edges", command=self.dump, highlightbackground='black', font=button_font,
                          padx=10, pady=10)
        button_window = self.canvas.create_window(size - size / 20, size - 2 * (size / 20), anchor=tk.SE, window=print_button)
        
        
        self.undo_stack = []
        self.nodes = []
        self.node_ids = []
        self.edges = []
        self.node_locations = []
        self.curr_edge = []
        self.curr_edge_location = None
        
        self.import_nodes_and_edges(in_nodes, in_edges)
        
        root.mainloop()

    def import_nodes_and_edges(self, in_nodes, in_edges):
        max_rand = int(self.size * 0.875)
        min_rand = int(self.size * 0.125)

        
        for i in in_nodes:
            self.draw_node_help(random.randint(min_rand, max_rand), random.randint(min_rand, max_rand), i)
            
        
            
            
    
    def dump(self, event=None):
        print("Nodes:", self.nodes)
        print("Edges:", self.edges)
        
        
        
    def toggle(self, event=None):
        # note toggling clears undo stack intentionally
        # dont want to draw an edge and then undo
        self.not_active = "Nodes" if self.not_active == "Edges" else "Edges"
        self.button.config(text=f"Switch to Adding {self.not_active}")
        # self.undo_stack = []

    def clear_edge(self, event):
        if self.not_active == "Nodes":
            self.curr_edge = []
            self.curr_edge_location = None
            [self.canvas.itemconfig(x, outline='white') for x in self.node_ids]
            
    
    
    def draw_node(self, event):
        x, y = event.x, event.y
        self.draw_node_help(x, y)
    
    def draw_node_help(self, x, y, text=None):
        # x, y = event.x, event.y
        if text is None:
            text = tkinter.simpledialog.askstring("Text Input", "Enter text:")
        if text:
            
            if (text in self.nodes):
                messagebox.showinfo("Repeat", "Warning: this node already exists. Use Command-z to undo")
                
            self.nodes.append(text)
            self.node_locations.append((x,y))
            
            my_text = self.canvas.create_text(x, y-20, text=text, fill='white')
            my_circle = self.canvas.create_oval(x-10, y-10, x+10, y+10, outline='white', width=2)
            
            self.node_ids.append(my_circle)
            self.undo_stack.append((my_text, my_circle))
            
            
    def undo(self, event):
        if len(self.undo_stack) > 0:
            
            items = self.undo_stack.pop()
            [self.canvas.delete(i) for i in items]
            
            if len(items) > 1:
                self.node_locations.pop()
                self.nodes.pop()
                self.node_ids.pop()
            
            else:
                self.edges.pop()
                
                
        else:
            messagebox.showinfo("Undo", "Nothing to undo")
            
    def find_closest_node(self, event, threshhold=30):
        # print("here")
        x, y = event.x, event.y
        best = 99999999999999
        best_index = -1
        best_location = (-1, -1)
        for i, n in enumerate(self.node_locations):
            nx, ny = n
            distance_from_click = ((nx - x)**2 + (ny - y)**2)**0.5
            if distance_from_click < threshhold:
                if distance_from_click < best:
                    best = distance_from_click
                    best_index = i
                    self.canvas.itemconfig(self.node_ids[best_index], outline='red')
                    self.curr_edge.append(self.nodes[best_index])
                    best_location = n
                    # add edge is from nodes[best_index]
        return best_location
    

    def line_adjust(self, x1, y1, x2, y2):
        # Calculate the distance between the centers of the circles
        dist_centers = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        
        # Calculate the unit vector along the line connecting the centers
        if dist_centers == 0:
            return x1 + 10, y1, x2 - 10, y2  # If the circles have the same center, return points on x-axis
        
        ux = (x2 - x1) / dist_centers
        uy = (y2 - y1) / dist_centers
        
        # Calculate the points on the line segment closest to the circles' perimeters
        x1_new = x1 + 10 * ux
        y1_new = y1 + 10 * uy
        x2_new = x2 - 10 * ux
        y2_new = y2 - 10 * uy
        
        return x1_new, y1_new, x2_new, y2_new


    def draw_edge(self, event):
        if self.curr_edge_location is not None:
            x1, y1 = self.curr_edge_location
            x2, y2 = self.find_closest_node(event)
            self.draw_edge_helper( x1, y1, x2, y2)
        
        else:
            self.curr_edge_location = self.find_closest_node(event)
            
            if self.curr_edge_location[0] == -1 and self.curr_edge_location[1] == -1:
                messagebox.showinfo("Node", "No node found")
                self.curr_edge_location = None
            
    
    def draw_edge_helper(self, x1, y1, x2, y2):

        if x2 == -1 and y2 == -1:
            messagebox.showinfo("Node", "No node found")
            return
        # TODO: should do math to make arrows appear on perimeter
        ax1, ay1, ax2, ay2 = self.line_adjust(x1, y1, x2, y2)
        my_line = self.canvas.create_line(ax1, ay1, ax2, ay2, arrow=tk.LAST) # maybe .FIRST
        self.undo_stack.append((my_line, ))
        
        
        self.curr_edge_location = None
        if (tuple(self.curr_edge) in self.edges):
            messagebox.showinfo("Repeat", "Warning: this edge already exists. Use Command-z to undo")
            
        self.edges.append(tuple(self.curr_edge))
        self.curr_edge = []
        [self.canvas.itemconfig(x, outline='white') for x in self.node_ids]
            
    
    def handle_click(self, event):
        if self.not_active == "Edges":
            # drawing nodes
            self.draw_node(event)
        else:
            self.draw_edge(event)
            
        # print(self.nodes, self.edges)
        
            
        
        
#TODO: work on better existing imports

#TODO: make things moveable
#TODO: have a edge and node counter

def main():
    drawer = Dag_Drawer()

    
if __name__ == "__main__":
    main()