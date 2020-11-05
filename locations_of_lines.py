import numpy as np
from bokeh.io import curdoc, show, output_notebook
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, ColorPicker, RadioButtonGroup
from bokeh.plotting import figure
from bokeh.embed import server_document

# to run:
# open terminal
# cd to directory containing locations_of_lines.py
# bokeh serve --show locations_of_lines.py

class LineFactory:
    """
    A class used to generate "Locations of Lines" artworks by Sol LeWitt

    Attributes
    ----------
    line_length : int
        length of lines
    line_gap : int
        length of gap between lines
    column_density : int
        how many columns to skip between drawn columns
    row_density : int
        how many rows to skip between drawn rows  
    """

    def __init__(self,line_length:int,line_gap:int,column_density:int,row_density:int):

        self.number_of_rows_cols = 1000 # hardcoded
        self.rows_cols = np.arange(self.number_of_rows_cols*3)
        self.line_length = line_length
        self.line_gap = line_gap
        self.row_density = 100-row_density
        self.column_density = 100-column_density

        self.make_lines()
    
    def make_lines(self,line_length:int=None,line_gap:int=None,row_density:int=None,column_density:int=None):
        """Update lines with new values and recreate lines. Used for update upon widget value changing.
        
        Parameters
        ----------
        line_length : int
            length of lines
        line_gap : int
            length of gap between lines
        column_density : int
            how many columns to skip between drawn columns
        row_density : int
            how many rows to skip between drawn rows  
        """
        if line_length:
            self.line_length = line_length
        if line_gap:
            self.line_gap = line_gap
        if row_density:
            self.row_density = 100-row_density
        if column_density:
            self.column_density = 100-column_density

        self.horizontal_lines_xs,self.horizontal_lines_ys = self._generate_all_lines(horizontal=True)
        self.vertical_lines_ys,self.vertical_lines_xs = self._generate_all_lines(horizontal=False)

    def _generate_row_col_lines(self,iter):
        """Create x and y coordinates for lines for a single row/column.

        Parameters
        ----------
        iter : int
            ith row/column of figure 
        
        Returns
        -------
        lines1 : np.array
            First set of coordinates for lines. 
        lines2 : np.array
            Second set of coordinates for lines
        """
        #make each row differ slightly
        start_jitter = np.random.choice(np.arange(self.line_length+self.line_gap)) 
        
        #grab coordinates
        coordinates1 = self.rows_cols[start_jitter::self.line_gap+self.line_length] 
        coordinates2 = self.rows_cols[start_jitter+self.line_length::self.line_gap+self.line_length] 
        
        #make sure x coordinate arrays match dimensions
        if coordinates1.shape[0] > coordinates2.shape[0]: 
            coordinates1 = coordinates1[0:-1]

        #combine and transpose
        lines1 = np.vstack((coordinates1,coordinates2)).T 

        #create matching coordinates
        lines2 = np.ones(lines1.shape)*iter

        return lines1,lines2

    def _generate_all_lines(self,horizontal=True):
        """Create x and y coordinates for every row/col of plot 
        
        Returns
        -------
        lines1 : list of lists
            First set of coordinates for lines.
            If generating horizontal lines, these are x-coordinates.
            If generating vertical lines, these are y-coordinates.
        lines2 : list of lists
            Second set coordinates for lines.
            If generating horizontal lines, these are y-coordinates.
            If generating vertical lines, these are x-coordinates.
        """
        if horizontal:
            density = self.row_density
        else:
            density = self.column_density

        for row_col in self.rows_cols[::density]:
            if row_col == 0:
                lines1,lines2 = self._generate_row_col_lines(row_col)
            else:
                a,b = self._generate_row_col_lines(row_col)
                lines1 = np.concatenate((lines1,a))
                lines2 = np.concatenate((lines2,b))
        lines1,lines2 = lines1.tolist(),lines2.tolist()
        return lines1,lines2
    
    def plot_lines(self):
        """Calls make_vertical and make_horizontal function to generate lines and create final plot."""

        #create figure
        plot = figure(
            plot_width=500, plot_height=500,
            x_range=(self.number_of_rows_cols,self.number_of_rows_cols*2),
            y_range=(self.number_of_rows_cols,self.number_of_rows_cols*2)
            )

        #plotting details
        plot.toolbar.logo = None
        plot.toolbar_location = None
        plot.axis.visible = False
        plot.grid.visible = False

        return plot

# Set up data
lines = LineFactory(
    line_length=250, line_gap=50,
    column_density=80, row_density=80)

line_thickness = 1

horizontal_source = ColumnDataSource(data=dict(
    horizontal_lines_xs=lines.horizontal_lines_xs,
    horizontal_lines_ys=lines.horizontal_lines_ys))

vertical_source = ColumnDataSource(data=dict(
    vertical_lines_xs=lines.vertical_lines_xs,
    vertical_lines_ys=lines.vertical_lines_ys))

# Set up plot
plot = lines.plot_lines()
horizontal_lines = plot.multi_line(xs = 'horizontal_lines_xs', ys='horizontal_lines_ys',source=horizontal_source,line_width=line_thickness,color='black')
vertical_lines = plot.multi_line(xs = 'vertical_lines_xs', ys='vertical_lines_ys',source=vertical_source,line_width=line_thickness,color='black')

# Set up widgets
# data widgets
line_length = Slider(title="Line Length", value=250, start=0, end=1000, step=10)
line_gap = Slider(title="Line Gap", value=50, start=0, end=1000, step=10)
row_density = Slider(title="Row Density", value=80, start=0, end=90, step=10)
column_density = Slider(title="Column Density", value=80, start=0, end=90, step=10)

# plotting widgets
row_color_widget = ColorPicker(title="Row Color")
column_color_widget = ColorPicker(title="Column Color")
row_color_widget.js_link('color', horizontal_lines.glyph, 'line_color')
column_color_widget.js_link('color', vertical_lines.glyph, 'line_color')

line_thickness = Slider(title="Line Thickness", value=1, start=0, end=10, step=1)
line_thickness.js_link('value', vertical_lines.glyph, 'line_width')
line_thickness.js_link('value', horizontal_lines.glyph, 'line_width')

# Set up callbacks
def update_data(attrname, old, new):

    # Get the current slider values
    ll = line_length.value
    lg = line_gap.value
    rd = row_density.value
    cd = column_density.value

    lines.make_lines(ll,lg,rd,cd)
    
    horizontal_source.data = dict(
        horizontal_lines_xs=lines.horizontal_lines_xs,
        horizontal_lines_ys=lines.horizontal_lines_ys)
        
    vertical_source.data = dict(
        vertical_lines_xs=lines.vertical_lines_xs,
        vertical_lines_ys=lines.vertical_lines_ys)
    
for w in [line_length, line_gap, row_density, column_density]:
    w.on_change('value', update_data)

# Set up layouts and add to document
inputs = column(line_length, line_gap, line_thickness, row_density, column_density, row_color_widget, column_color_widget)

curdoc().add_root(row(inputs, plot, width=800))