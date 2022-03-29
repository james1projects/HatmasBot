"""Tkinter Helper.

Used to make creating tkinter widgets easier.
"""

from tkinter import ttk, VERTICAL, Text
from tkinter import WORD, StringVar, Listbox

# pylint: disable=too-many-instance-attributes


class TkinterHelper():
    """Used to make creating tkinter widgets easier."""

    def __init__(self, frame):
        """Initialize variables for TkinterHelper."""
        self.row = 0
        self.column = 0
        self.rowspan = 1
        self.columnspan = 1
        self.frame = frame
        self.sticky = "W"
        self.padx = 1
        self.pady = 1
        self.string_var = None
        self.text_height = 10
        self.text_width = 10
        self.listbox_height = 5
        self.listbox_width = 5

    def next_row(self, starting_column=0):
        """Move to next row and resets column.

        Parameters
        ----------
        starting_column: int, optional
            The column to reset to. The default is 0.
        """
        self.row += 1
        self.reset_column(column=starting_column)

    def next_column(self, columns_to_skip=1):
        """Move to next column."""
        self.column += columns_to_skip

    def reset_column(self, column=0):
        """Reset the column.

        Parameters
        ----------
        column : int, optional
            DESCRIPTION. The default is 0.
        """
        self.column = column

    def create_scrollbar_grid(self, function, orient=VERTICAL):
        """Create a ttk scrollbar that is grided.

        Parameters
        ----------
        command : function, optional
            function for the scrollbar.
        orient : ENUM, optional
            VERTICAL/HORIZONTAL. The orientation of the scrollbar.
            The default is VERTICAL.

        Returns
        -------
        scrollbar_new : ttk.Scrollbar
            Newly created Scrollbar object.
        """
        scrollbar_new = ttk.Scrollbar(self.frame, orient=orient, command=function,
                                      y_scroll_command=None)
        scrollbar_new.grid(row=self.row, column=self.column,
                           rowspan=self.rowspan,
                           columnspan=self.columnspan, sticky=self.sticky)

        return scrollbar_new

    def create_checkbox_grid(self, text, int_var, function):
        """Create a ttk checkbox that is grided.

        Parameters
        ----------
        text : String
            String for the label of checkbox.
        int_var : IntVar
            IntVar that keeps track of checkbox state.
        function : function
            function to be run when checkbox is clicked.

        Returns
        -------
        checkbox_new : ttk.Checkbutton
            The new checkbox.

        """
        checkbox_new = ttk.Checkbutton(self.frame, text=text, variable=int_var,
                                       command=function)
        checkbox_new.grid(row=self.row, column=self.column, pady=self.pady,
                          padx=self.padx, sticky=self.sticky)

        return checkbox_new

    def create_button_grid(self, text, function):
        """Create a ttk button that is grided.

        Parameters
        ----------
        text : String
            Text on the button.
        command : function
            function to be run.

        Returns
        -------
        button_new : ttk.Button
            The new Button.

        """
        button_new = ttk.Button(self.frame, text=text, command=function)
        button_new.grid(sticky=self.sticky, row=self.row, column=self.column, pady=self.pady,
                        padx=self.padx, rowspan=self.rowspan, columnspan=self.columnspan)

        return button_new

    def create_label_grid(self, text=""):
        """Create a ttk Label.

        Parameters
        ----------
        text : String, optional
            Text on the Label.
            The default is "".

        Returns
        -------
        label_new : ttk.Label
            The new Label.

        """
        label_new = ttk.Label(self.frame, text=text)
        label_new.grid(sticky=self.sticky, row=self.row, column=self.column, rowspan=self.rowspan,
                       columnspan=self.columnspan, pady=self.pady, padx=self.padx)

        return label_new

    def create_entry_grid(self, text="", entry_changed_function=None):
        """Create entry that is grided.

        Parameters
        ----------
        text : String, optional
            Text on entry. The default is "".
        entry_changed_function : TYPE, optional
            Function to be run if the entry is changed. The default is True.

        Returns
        -------
        entry_new : ttk.Entry
            The new Entry.

        """
        width = 40
        entry_new = ttk.Entry(self.frame, text=text, width=width)
        entry_new.grid(row=self.row, column=self.column, rowspan=self.rowspan,
                       columnspan=self.columnspan)

        if entry_changed_function is not None:
            self.string_var = StringVar()
            self.string_var.trace("w", lambda name, index, mode, sv=self.string_var:
                                  entry_changed_function(sv))
            entry_new.config(textvariable=self.string_var)

        return entry_new

    def create_text_grid(self):
        """Create tkinter Text that is grided.

        Returns
        -------
        text_new : tkinter Text
            The new Text.
        """
        text_new = Text(self.frame, height=self.text_height, width=self.text_width)
        text_new.configure(state="normal", wrap=WORD)
        text_new.grid(row=self.row, column=self.column, rowspan=self.rowspan, sticky=self.sticky,
                      columnspan=self.columnspan, padx=self.padx, pady=self.pady,)

        return text_new

    def create_listbox_grid(self, select_function=None):
        """Create listbox that is grided.

        Parameters
        ----------
        select_function : function, optional
            Function to be ran when listbox has a selection made.
            The default is None.

        Returns
        -------
        listbox_new : tkinter Listbox
            tkinter Listbox object.
        """
        listbox_new = Listbox(self.frame, height=self.listbox_height, width=self.listbox_width)
        if select_function is not None:
            listbox_new.bind('<<ListboxSelect>>', select_function)
        listbox_new.grid(row=self.row, column=self.column, rowspan=self.rowspan,
                         columnspan=self.columnspan, sticky=self.sticky)

        return listbox_new
