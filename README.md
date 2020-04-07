# kivy_qztable
A table/grid widget for kivy

As of April 2020 Kivy lacks a grid/table widget
This is a severe limitation when trying to use Kive as a gui library for any data science AI project because there are a large number of data structures that require a grid to be displayed:
  - Numpy arrays
  - Lists
  - Dataframes
  
  This component is aimed to fill that gap, but specially considering its usage in data science where the number of columns might reach the hundreds and the number of rows might reach the thousands. 
  Hence , the grid creates only the widgets that are visible within the widget boundaries. This will save tons of memory at the expense of extra rendering time ( which is not really a problem in a modern pc , but might be a problem for smaller devices like mobile phones). 
  
  The main features of the table are the following:
  
    - Horizontal and vertical scroll bars
    - Multiple selection of rows and columns ( shift+ select is still missing in beta 0.9)
    - Built-in support for displaying dataframe , lists and numpy arrays
    - Column and Row sizing
    - Virtual rows to display arbiitrary data within the virtual rows
    - A table model class to be used when the data is not a list, array or dataframe
    - The default widget for the table is a CellLabel.
    - When using a TableModel any widget can be used
    - When NOT using a TableModel , any widget that follows the CellWidget protocol can be used
    
    The CellWidget protocol requires the following methods to be implemented
    
    def get_value(self)->Any: #returns the value of the widget, usually the text value
    def set_value(self,value:Any):  #Sets the value of the widget, usually it will put the value in the text property
    def on_value_changed(self,instance,value): #defines an event that is triggered when the value of the widget is changed
    
   
    
