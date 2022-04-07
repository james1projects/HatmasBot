"""HatBot but with a GUI and the option to easily change settings.

TwitchBotGui() creates the window.

Version 1.1
"""
from datetime import datetime
import HatBot_Twitch
import HatBotConfig
import os
import sys
import webbrowser
import requests
import SmiteAPIExtended
import tkinter
from tkinter import messagebox, PhotoImage
from tkinter import IntVar, Grid, Toplevel
from tkinter import Frame, END
from tkinter import font
from tkinter_helper import TkinterHelper

# determine if application is a script file or frozen exe
# and set the current directory (current_directory) appropriately
if getattr(sys, 'frozen', False):
    current_directory = os.path.dirname(sys.executable)
elif __file__:
    current_directory = os.path.dirname(__file__)

# COLOR SETTINGS
color_text = "#D3D3D3"
title_font_size = "20"
normalFontSize = "10"


class TwitchBotGui(HatBot_Twitch.TwitchBot):
    """HatBot but with a GUI."""

    def __init__(self, oConsoleWindow):
        print("inside TwitchBotGui")
        # oConsoleWindow would be an object of class MainWindow()
        self.oConsoleWindow = oConsoleWindow
        super().__init__()

    def log(self, text, logToGuiConsole=True, isBolded=False):
        r"""Log some text.

        Parameters
        ----------
        text : TYPE
            DESCRIPTION.
        logToGuiConsole : TYPE, optional
            DESCRIPTION. The default is True.
        isBolded : TYPE, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        None.

        """
        text = text + "\n"
        print(text, end='')
        if (logToGuiConsole and self.oConsoleWindow is not None):
            message_dictionary = {}
            message_dictionary['texts'] = [text]
            message_dictionary['colors'] = [color_text]
            message_dictionary['bold'] = [isBolded]
            self.oConsoleWindow.console_list.append(message_dictionary)

    def log_colored_message(self, list_strings, list_colors=None,
                            list_emotes=None, logToGuiConsole=True):
        """Log a colored message.

        Parameters
        ----------
        list_strings : list
            DESCRIPTION.
        list_colors : list, optional
            DESCRIPTION. The default is None.
        list_emotes : list, optional
            DESCRIPTION. The default is None.
        logToGuiConsole : boolean, optional
            DESCRIPTION. The default is True.

        Returns
        -------
        None.

        """
        message_dictionary = {}
        text_list = list_strings
        color_list = list_colors
        emote_list = list_emotes
        if (logToGuiConsole and self.oConsoleWindow is not None):
            message_dictionary['texts'] = text_list
            message_dictionary['colors'] = color_list
            message_dictionary['emotes'] = emote_list
            self.oConsoleWindow.console_list.append(message_dictionary)

    def log_twitch_message(self, displayname, message,
                           displayname_color=color_text, list_emotes=None):
        """Log a twitch message to the console.

        Parameters
        ----------
        displayname : String
            DESCRIPTION.
        message : String
            DESCRIPTION.
        displayname_color : String, optional
            DESCRIPTION. The default is color_text.
        list_emotes : list, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        bold_font = font.Font(self.oConsoleWindow.console, self.oConsoleWindow.console.cget("font"))
        bold_font.configure(weight="bold")
        # default_chat_message_color = "#FFFFFF"

        self.oConsoleWindow.console.configure(state='normal')
        self.oConsoleWindow.console.insert(END, displayname, displayname_color)
        self.oConsoleWindow.console.tag_config(displayname_color, foreground=displayname_color,
                                               font=bold_font)

        self.oConsoleWindow.console.insert(END, ": ", color_text)
        start_message_pos = self.oConsoleWindow.console.index("end-1c")
        self.oConsoleWindow.console.insert(END, message, color_text)
        self.oConsoleWindow.console.tag_config(color_text, foreground=color_text)
        for emote in list_emotes:
            if emote == "":
                continue

            emote_id = emote.split(":")[0]

            emote_indexes = emote.split(":")[1].split(",")

            for indexes in emote_indexes:
                emote_index_start = int(indexes.split("-")[0])
                emote_index_end = int(indexes.split("-")[1]) + 1

                emote_name = message[emote_index_start:emote_index_end]

            if emote_name not in self.oConsoleWindow.emotes_dict:
                # there is not an easy way to check if the emote is animated..
                emote_format = "static"

                emote_theme = "dark"
                emote_scale = "1.0"

                url = ("https://static-cdn.jtvnw.net/emoticons/v2/" +
                       emote_id + "/" + emote_format + "/"
                       + emote_theme + "/" + emote_scale)
                print(url)
                print("EMOTE NAME:", emote_name)
                response = requests.get(url)
                if response.status_code == 200:
                    image = response.content
                    # print(image)
                    print("IMAGE TYPE", type(image), "\n")
                    image = bytes(image)
                    if emote_format == "static":
                        emote_image = PhotoImage(data=image, format="png")
                    else:
                        emote_image = PhotoImage(data=image, format="gif")
                        print(emote_image)
                    self.oConsoleWindow.emotes_dict[emote_name] = emote_image
            else:
                emote_image = self.oConsoleWindow.emotes_dict[emote_name]

            for indexes in emote_indexes:
                emote_index_start = int(indexes.split("-")[0])
                emote_index_end = int(indexes.split("-")[1]) + 1

                # emote_pos_start = start_message_pos
                # emote_pos_end = str(float(start_message_pos) + float(emote_index_end / 10))
                emote_pos_start = self.oConsoleWindow.console.search(
                    emote_name, index=start_message_pos, stopindex=END)
                emote_pos_end = ('%s+%dc' % (emote_pos_start, len(emote_name)))
                # print("START:", emote_pos_start, "\nEND:", emote_pos_end)
                if (emote_pos_start != -1 and emote_pos_end != -1):
                    self.oConsoleWindow.console.delete(emote_pos_start,
                                                       emote_pos_end)
                    self.oConsoleWindow.console_insert_emote(
                        self.oConsoleWindow.emotes_dict.get(emote_name, None),
                        emote_pos_start)

        self.oConsoleWindow.console.configure(state='disabled')


class Form():
    """Form to hold tkinter widgets."""

    def __init__(self, frame):
        self.frame = frame


class Window(Form):
    """Window for tkinter."""

    def __init__(self, oParentWindow, title="", createWindow=True):
        self.oParentWindow = oParentWindow
        if oParentWindow != self:
            self.root = oParentWindow.root
        else:
            self.root = None

        if createWindow:
            self.create_window(self.root)

        super().__init__(self.window)

        if title != "":
            self.window.title(title)

    def create_window(self, root):
        """Create new window."""
        self.root = root
        if root is None:
            # For main window, the root and window are the same.
            self.root = tkinter.Tk()
            self.window = self.root
        else:
            self.window = Toplevel(self.oParentWindow.window)

        self.set_window_image()

        # self.window.configure(bg=color_background)
        self.window.wm_protocol("WM_DELETE_WINDOW", self.close_window)
        self.window.lift()

    def close_window(self):
        """Close window."""
        print("Super close window")
        self.window.destroy()

    def set_window_image(self):
        """Set window image to hat."""
        config = HatBotConfig.HatBotConfig()
        path_image_hat = config.loadOption(config.SECTION_SETTINGS,
                                           config.PATH_ICON_HAT)
        if os.path.exists(path_image_hat):
            image_hat = PhotoImage(file=path_image_hat)
            self.window.tk.call('wm', 'iconphoto', self.window._w, image_hat)


class MainWindow(Window):
    """Main window for Hat Bot GUI."""

    def __init__(self):
        print("Creating Root Window..")
        self.oSmiteClient = None
        # Contains a list of console_dictionary
        self.console_list = []
        self.emotes_dict = {}
        # Console dictionary is a dictionary containing
        # 'texts': list of texts
        # 'colors': list of colors
        # 'emotes'L list of emotes
        # it does not need to contain colors or emotes and will have default values.
        # Super is called after window is created for MainWindow
        self.main_window_open = True
        super().__init__(oParentWindow=self, title="Hat's Twitch Bot")
        self.root.tk.call("source", "sun-valley.tcl")
        self.root.tk.call("set_theme", "dark")

        # settingsWindow contains the object of the settings window. None when not opened.
        self.settingsWindow = None
        self.twitchBot = None  # When the bot is running, this is an object from HatBot_Twitch
        self.consoleMessages = 0
        self.CreateInterface()

    def main_loop(self):
        """Enter main loop for program logic."""
        # Start the mainloop of the window...
        print("Entering window loop...")
        smite_portrait_time_stamp = datetime.utcnow()
        smite_portrait_delay = 0
        try:
            while (self.main_window_open and self.window is not None):
                if (self.main_window_open and self.window is not None):
                    self.window.update()
                if (self.main_window_open and self.window is not None):
                    self.window.update_idletasks()
                    self.bot_main()
                    self.check_console()
                config = HatBotConfig.HatBotConfig()
                feature_smite_portrait = config.load_option(
                    config.SECTION_TOGGLED_FEATURES, config.FEATURE_SMITE_PORTRAIT)
                if feature_smite_portrait:
                    # print((datetime.now() - smite_portrait_time_stamp).total_seconds())
                    if (datetime.utcnow() - smite_portrait_time_stamp).total_seconds() > smite_portrait_delay:
                        smite_portrait_time_stamp = datetime.utcnow()
                        smite_username = config.load_option(
                            config.SECTION_SMITE_API, config.SMITE_USERNAME)
                        if smite_username != "":
                            smite_client = SmiteAPIExtended.SmiteAPI()
                            smite_portrait_delay = smite_client.update_god_portrait(smite_username)
                        else:
                            smite_portrait_delay = 10
        except Exception as e:
            print(e)

        print("END")

    def CreateInterface(self):
        """Create the interface for MainWindow with console and other options."""
        config = HatBotConfig.HatBotConfig()
        tk_helper = TkinterHelper(self.frame)
        tk_helper.sticky = "NSWE"
        # Set the window image to a hat
        self.set_window_image()

        # Create the settings button
        self.button_settings = tk_helper.create_button_grid("Settings",
                                                            function=self.open_settings)

        # Create Main Label
        tk_helper.sticky = "NS"
        tk_helper.next_column()
        tk_helper.columnspan = 2
        self.label_title = tk_helper.create_label_grid("Hat's Twitch Bot")
        self.label_title.config(font=(self.label_title.cget("font"),
                                      title_font_size))

        # Create Console for Twitch Chat
        tk_helper.next_row()
        tk_helper.text_width = 100
        tk_helper.text_height = 25
        tk_helper.columnspan = 4
        self.console = tk_helper.create_text_grid()
        self.console.config(state="disabled")

        tk_helper.sticky = "nsw"
        tk_helper.next_column(columns_to_skip=3)
        tk_helper.columnspan = 1
        # Create scrollbar for the console for Twitch Chat
        self.scrollbar_console = tk_helper.create_scrollbar_grid(
            function=self.console.yview)
        self.console.config(yscrollcommand=self.scrollbar_console.set)

        # Create start button for starting the Twitch Bot
        tk_helper.next_row()
        self.button_start = tk_helper.create_button_grid("Start",
                                                         function=self.start_twitch_bot)

        # Create auto start visual
        tk_helper.sticky = "W"
        tk_helper.next_column()
        self.isAutoStart = IntVar()
        self.checkbox_autoStart = tk_helper.create_checkbox_grid("autostart",
                                                                 int_var=self.isAutoStart,
                                                                 function=self.toggle_auto_start)

        # Create stop button for stopping and disconnecting the Twitch Bot
        tk_helper.sticky = "NS"
        tk_helper.next_column(columns_to_skip=1)
        self.button_stop = tk_helper.create_button_grid("Stop",
                                                        function=self.stop_twitch_bot)

        Grid.rowconfigure(self.window, 1, weight=1)
        Grid.columnconfigure(self.window, 1, weight=1)

        # if (feature_smitePortrait):
        #    #Start the smite portrait loop
        #    self.window.after(1, self.SmitePortraitLoop)

        # self.window.after(2, self.check_console)
        # self.after_commands.append(self.check_console)

        # Set the function for when closing out of the window
        # self.window.wm_protocol("WM_DELETE_WINDOW", self.close_window)

        # Correctly set the auto start to what it is in the config.
        if (int(config.loadOption(config.SECTION_SETTINGS,
                                  config.OPTION_AUTOSTART))) == 1:
            self.isAutoStart.set(1)
            self.start_twitch_bot()

    def toggle_auto_start(self):
        """Toggle auto start for the bot."""
        print("Toggling AutoStart: ", self.isAutoStart.get())
        config = HatBotConfig.HatBotConfig()
        config.saveOption(config.SECTION_SETTINGS, config.OPTION_AUTOSTART,
                          str(self.isAutoStart.get()))
        if self.isAutoStart.get() == 1:
            self.log("Bot will now auto start when the program is launched.\n")
        else:
            self.log("Bot will no longer auto start when the program is launched.\n")

    def start_twitch_bot(self):
        """Start twitch bot."""
        if self.twitchBot is None:
            self.log("Starting Bot...\n\n")
            if HatBot_Twitch.validate_token():
                self.twitchBot = TwitchBotGui(oConsoleWindow=self)
                self.twitchBot.stop = False
            else:
                self.log("Error: There is an issue with the bots oauth token." +
                         "\nOpen settings and click \"Get my oauth token\"" +
                         " for your twitch bot.\n")
        else:
            self.log("Bot is already running.\n")

    def stop_twitch_bot(self):
        """Stop twitch bot."""
        if self.twitchBot is not None:
            self.log("Disconnecting Bot from Twitch...\n\n")
            self.twitchBot.stop = True
            self.twitchBot.exit_bot()
            self.twitchBot = None
            self.log("Bot has disconnected from Twitch and is no longer running.\n")

        else:
            self.log("Twitch Bot is not running.\n")

    def bot_main(self):
        """Enter Main logic for twitch bot. Should be called in a loop."""
        if self.twitchBot is not None:
            self.twitchBot.main()

    def open_settings(self):
        """Open settings for Hat Bot."""
        if self.settingsWindow is None:
            self.settingsWindow = SettingsWindow(oParentWindow=self)
        else:
            print("Settings page is already opened.")

    def log(self, text, end="\n"):
        """Log text."""
        text = text + end
        print(text, end='')
        message_dictionary = {}
        message_dictionary['texts'] = [text]
        message_dictionary['colors'] = [color_text]
        self.console_list.append(message_dictionary)

    def check_console(self):
        """Check console messages and update pending ones."""
        self.console.configure(state='normal')
        while len(self.console_list) > 0:
            console_dictionary = self.console_list.pop(0)
            text_list = console_dictionary['texts']
            color_list = console_dictionary['colors']
            # emote_list = console_dictionary.get('emotes', None)

            for i in range(0, len(text_list)):
                text = text_list[i]
                color = color_list[i]
                self.console.insert(END, text, color)
                self.console.tag_config(color, foreground=color)

        self.console.configure(state='disabled')
        if self.scrollbar_console.get()[1] > 0.9:
            self.console.see("end")

    def console_insert_emote(self, emote_image, position):
        """Insert image into console, usually emotes.

        Parameters
        ----------
        emote_image : TYPE
            DESCRIPTION.
        position : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if emote_image is not None:
            self.console.image_create(position, image=emote_image)
        return emote_image  # prevents the garbage detector removing emote_image?

    def smite_portrait_loop(self):
        """Enter logic for replacing smite portrait with current god."""
        print("Checking God Portrait...")
        try:
            delay = self.oSmiteClient.UpdateGodPortrait("Hatmaster")
        except Exception as e:
            print("Error in SmitePortraitLoop.\n", e)
            delay = 10000
        print(delay)

    def close_window(self):
        """Close window."""
        print("Goodbye.")
        try:
            self.stop_twitch_bot()
        except Exception as e:
            print("error when exiting bot\n", e)

            # self._window_open = False
        super().close_window()


class SettingsWindow(Window):
    """Settings window class."""

    def __init__(self, oParentWindow, title=""):
        # selected settings from ListBox
        self.TWITCH_BOT_CREDENTIALS = "Twitch Bot Credentials"
        self.CHARACTER_REQUEST_SETTINGS = "Character Request Settings"
        self.SMITE_API_SETTINGS = "Smite API Settings"

        self.oParentWindow = oParentWindow
        self.root = self.oParentWindow.root
        super().__init__(oParentWindow)
        self.oSettingsPage = TwitchSettingsPanel(oWindow=self)
        self.window.resizable(width=False, height=False)
        self.init_list_box()

    def init_list_box(self):
        """Initialize listbox for settings window."""
        # config = HatBotConfig.HatBotConfig()
        # Create Listbox for settings and extra module settings
        tk_helper = TkinterHelper(self.window)
        tk_helper.listbox_width = 30
        tk_helper.listbox_height = 10
        tk_helper.sticky = "NSWE"
        self.listbox_settings = tk_helper.create_listbox_grid(
            select_function=self.listbox_settings_select)
        self.listbox_settings.insert(END, "Twitch Bot Credentials")
        self.listbox_settings.insert(END, "Character Request Settings")
        self.listbox_settings.insert(END, "Smite API Settings")

    def listbox_settings_select(self, event):
        """Call when item in listbox is selected."""
        config = HatBotConfig.HatBotConfig()

        def destroy_old_settings_page():
            if self.oSettingsPage is not None:
                self.oSettingsPage.destroy()

        # oNewSettingsPage = None
        sel = self.listbox_settings.curselection()
        if len(sel) >= 1:
            sel = sel[0]
            selected_text = self.listbox_settings.get(sel)
            title = "None Selected"
            if self.oSettingsPage is not None:
                title = self.oSettingsPage.title

            # If Twitch Bot Credentials is selected and we are not on that settings page...
            if (selected_text == self.TWITCH_BOT_CREDENTIALS
                    and title != self.TWITCH_BOT_CREDENTIALS):
                destroy_old_settings_page()
                print("Change to Twitch Bot Credentials")
                self.oSettingsPage = TwitchSettingsPanel(oWindow=self)
            elif (selected_text == self.CHARACTER_REQUEST_SETTINGS
                  and title != self.CHARACTER_REQUEST_SETTINGS
                  and config.loadOption(config.SECTION_TOGGLED_FEATURES,
                                        config.FEATURE_CHARACTER_REQUEST)):
                print("Change to Character Requests")
                destroy_old_settings_page()
                self.oSettingsPage = CharacterRequestSettings(oWindow=self)
            elif (selected_text == self.SMITE_API_SETTINGS
                  and title != self.SMITE_API_SETTINGS
                  and config.loadOption(config.SECTION_TOGGLED_FEATURES,
                                        config.FEATURE_SMITE_API)):
                print("Change to Smite API Settings")
                destroy_old_settings_page()
                self.oSettingsPage = SmiteApiSettingsPanel(oWindow=self)

    def close_window(self):
        """Close window."""
        if self.oSettingsPage is not None:
            if self.oSettingsPage.is_entry_changed:
                save_changes = messagebox.askyesno(title="Save Changes?",
                                                   message="Do you want to save your changes?")
                if save_changes:
                    self.oSettingsPage.save_settings(exit_settings=False)

        print("Close settings window")
        self.oParentWindow.settingsWindow = None
        super().close_window()


class Panel(Form):
    """Panel containing tkinter widgets."""

    def __init__(self, oWindow, row=0, column=0, rowspan=1, columnspan=1, sticky="NW"):
        self.oWindow = oWindow
        self.window = oWindow.window
        self.root = oWindow.root
        self.panel = Frame(self.window)
        self.panel.grid(row=row, column=column, rowspan=rowspan,
                        columnspan=columnspan, sticky=sticky)
        self.is_entry_changed = False
        super().__init__(self.window)

    def destroy(self):
        """Destroy panel."""
        self.panel.destroy()

    def entry_changed(self, string_var):
        """When entry is changed. Used for testing if settings need to be saved."""
        self.is_entry_changed = True


class TwitchSettingsPanel(Panel):
    """Twitch Settings Panel for bot."""

    def __init__(self, oWindow):
        super().__init__(oWindow, row=0, column=2, rowspan=1, columnspan=1)
        print("TwitchSettings() init")
        self.isTokenHidden = True
        self.title = self.oWindow.TWITCH_BOT_CREDENTIALS

        tk_helper = TkinterHelper(self.panel)
        tk_helper.sticky = "NSWE"
        # Channel username and entry
        self.label_channelUsername = tk_helper.create_label_grid("Twitch.tv/")
        tk_helper.next_column()
        self.entry_channelUsername = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Twitch Bot Username and Entry
        tk_helper.next_row()
        self.label_botUsername = tk_helper.create_label_grid(
            "Twitch Bot Username:")
        tk_helper.next_column()
        self.entry_botUsername = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Twitch oauth token
        tk_helper.next_row()
        self.label_token = tk_helper.create_label_grid("oauth Token: ")
        tk_helper.next_column()
        self.entry_token = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)
        self.entry_token.config(show="*")
        tk_helper.next_column()
        self.button_showToken = tk_helper.create_button_grid(
            "Show", function=self.toggle_show_token)
        self.button_showToken.configure(width=6)

        tk_helper.next_row()
        tk_helper.columnspan = 3
        # Button to get oauth token and show the user where to get it.
        self.button_getToken = tk_helper.create_button_grid(
            "Get my oauth token", function=self.get_token)

        tk_helper.next_row(starting_column=1)
        tk_helper.columnspan = 1
        self.button_saveSettings = tk_helper.create_button_grid(
            "Save and Close Settings", function=self.save_settings)
        self.load_settings()

    def toggle_show_token(self):
        """Toggle whether to show the oauth token or not."""
        if self.isTokenHidden:
            self.entry_token.config(show="")
            self.button_showToken.config(text="Hide")
            self.isTokenHidden = False
        else:
            self.entry_token.config(show="*")
            self.button_showToken.config(text="Show")
            self.isTokenHidden = True

    def load_settings(self):
        """Load Twitch Settings."""
        # print("Load Twitch Setttings")
        config = HatBotConfig.HatBotConfig()
        # pylint: disable=line-too-long
        self.entry_channelUsername.insert(0, config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_CHANNEL_NAME))
        self.entry_botUsername.insert(0, config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_BOT_USERNAME))
        self.entry_token.insert(0, config.loadOption(config.SECTION_CREDENTIALS, config.OPTION_OAUTH_TOKEN))
        self.is_entry_changed = False

    def save_settings(self, exit_settings=True):
        """Save Twitch Panel Settings.

        Parameters
        ----------
        exit_settings : TYPE, optional
            Whether to close out of the settings or not. The default is True.

        Returns
        -------
        None.

        """
        # print("Save settings")
        config = HatBotConfig.HatBotConfig()
        # pylint: disable=line-too-long
        config.saveOption(config.SECTION_CREDENTIALS, config.OPTION_CHANNEL_NAME, self.entry_channelUsername.get())
        config.saveOption(config.SECTION_CREDENTIALS, config.OPTION_BOT_USERNAME, self.entry_botUsername.get())
        config.saveOption(config.SECTION_CREDENTIALS, config.OPTION_OAUTH_TOKEN, self.entry_token.get())

        self.is_entry_changed = False

        if exit_settings:
            self.oWindow.close_window()

    def destroy(self):
        """Destroy Twitch Settings Panel."""
        if self.is_entry_changed:
            save_changes = messagebox.askyesno(title="Save Changes?",
                                               message="Do you want to save your changes?")
            if save_changes:
                self.save_settings(exit_settings=False)

        self.panel.destroy()
        self.is_entry_changed = False
        del self

    def get_token(self):
        """Get oauth token."""
        webbrowser.open("https://twitchapps.com/tmi/")
        # pylint: disable=line-too-long
        self.oWindow.oParentWindow.log("1) Open https://twitchapps.com/tmi/ in your browser.")
        self.oWindow.oParentWindow.log("2) Click Connect, and login using the account you want this bot to connect to and send messages with.")
        self.oWindow.oParentWindow.log("3) Copy the entire token including oauth into the settings for oauth Token.")
        self.oWindow.oParentWindow.log("4) Save the settings.\n")


class CharacterRequestSettings(Panel):
    """Character Request Settings Panel."""

    def __init__(self, oWindow):
        super().__init__(oWindow, row=0, column=1, rowspan=1, columnspan=1)
        self.title = self.oWindow.CHARACTER_REQUEST_SETTINGS

        tk_helper = TkinterHelper(self.panel)
        tk_helper.sticky = "E"
        # COMMAND SETTINGS FOR CHARACTER REQUESTS
        # Request Command
        self.label_commandRequest = tk_helper.create_label_grid("Mod Request Character Command:")
        tk_helper.next_column()
        self.entry_commandRequest = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Remove Command
        tk_helper.next_row()
        self.label_commandRemove = tk_helper.create_label_grid("Mod Remove Character Command:")
        tk_helper.next_column()
        self.entry_commandRemove = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Replace Command
        tk_helper.next_row()
        self.label_commandReplace = tk_helper.create_label_grid("Mod Replace Character Command:")
        tk_helper.next_column()
        self.entry_commandReplace = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Insert Command
        tk_helper.next_row()
        self.label_commandInsert = tk_helper.create_label_grid("Mod Insert Character Command:")
        tk_helper.next_column()
        self.entry_commandInsert = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Clear Command
        tk_helper.next_row()
        self.label_commandClear = tk_helper.create_label_grid("Mod Clear Character Command:")
        tk_helper.next_column()
        self.entry_commandClear = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Show Character List Command
        tk_helper.next_row()
        self.label_commandList = tk_helper.create_label_grid("User Show Character List:")
        tk_helper.next_column()
        self.entry_commandList = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # How to request Command
        tk_helper.next_row()
        self.label_commandHowToRequest = tk_helper.create_label_grid("How to Request Command:")
        tk_helper.next_column()
        self.entry_commandHowToRequest = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)
        self.reg_entry_commandHowToRequestSV = self.panel.register(
            self.entry_edit_how_to_request)
        # pylint: disable=line-too-long
        self.entry_commandHowToRequest.config(validate="focusout", validatecommand=(self.reg_entry_commandHowToRequestSV, "%P"))

        # How to request response
        tk_helper.next_row()
        self.label_howToRequestText = tk_helper.create_label_grid("!howtorequest response:")
        # Text space for how to request
        tk_helper.text_height = 5
        tk_helper.text_width = 40
        tk_helper.next_column()
        tk_helper.sticky = "NSWE"
        self.text_howToRequest = tk_helper.create_text_grid()
        # self.text_howToRequest = Text(self.panel, height=5, width=40)
        # self.text_howToRequest.grid(row=row, column=self.columnstart+1, sticky="nsew", columnspan=1, padx=10, pady=10)

        # Text for when there is no god request
        tk_helper.sticky = "E"
        tk_helper.next_row()
        self.label_noNextCharacter = tk_helper.create_label_grid("Text when there is not a request:")
        tk_helper.next_column()
        self.entry_noNextCharacter = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Character Type. Smite would be "God", Dead by daylight would be Killer or Survivor or Character
        tk_helper.next_row()
        self.label_characterType = tk_helper.create_label_grid("Character Type:")
        tk_helper.next_column()
        self.entry_characterType = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Image Format, for now do not display this option
        # row += 1
        # self.label_characterImageFormat = self.create_label_grid(text="Character Image Format:", row=row, column=self.columnstart, frame=self.panel, sticky="e")
        # self.entry_characterImageFormat = self.create_entry_grid(text="", row=row, column=self.columnstart+1, frame=self.panel)
        # TODO For now the image format is hidden, but maybe implement a better way of customizeability for it.
        # self.label_characterImageFormat.grid_forget()
        # self.entry_characterImageFormat.grid_forget()
        tk_helper.next_row(starting_column=1)
        tk_helper.sticky = 'nswe'
        # Save button
        self.button_saveSettings = tk_helper.create_button_grid(
            "Save and Close Settings", function=self.save_settings)
        self.load_settings()

    def load_settings(self):
        """Load character request settings."""
        # Load commands from config.ini
        # print("Load Command Settings")
        config = HatBotConfig.HatBotConfig()

        self.entry_commandRequest.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REQUEST))
        self.entry_commandRemove.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REMOVE))
        self.entry_commandReplace.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REPLACE))
        self.entry_commandInsert.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_INSERT))
        self.entry_commandClear.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_CLEAR))
        self.entry_commandList.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_LIST))
        self.entry_commandHowToRequest.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_HOW_TO_REQUEST))
        self.label_howToRequestText['text'] = config.loadOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_HOW_TO_REQUEST)

        self.entry_noNextCharacter.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_RESPONSE_NO_NEXT))
        self.text_howToRequest.insert(END, config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_RESPONSE_HOW_TO_REQUEST))
        self.entry_characterType.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_TYPE))
        # self.entry_characterImageFormat.insert(0, config.loadOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_IMAGE_FORMATS))
        self.is_entry_changed = False

    def save_settings(self, exit_settings=True):
        """Save Character Request Settings."""
        config = HatBotConfig.HatBotConfig()
        # Save command settings
        config.saveOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REQUEST, self.entry_commandRequest.get())
        config.saveOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REMOVE, self.entry_commandRemove.get())
        config.saveOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_REPLACE, self.entry_commandReplace.get())
        config.saveOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_INSERT, self.entry_commandInsert.get())
        config.saveOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_CLEAR, self.entry_commandClear.get())
        config.saveOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_LIST, self.entry_commandList.get())
        config.saveOption(config.SECTION_CHARACTER_REQUEST_COMMANDS, config.COMMAND_CHARACTER_HOW_TO_REQUEST, self.entry_commandHowToRequest.get())
        config.saveOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_RESPONSE_NO_NEXT, self.entry_noNextCharacter.get())
        config.saveOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_RESPONSE_HOW_TO_REQUEST, self.text_howToRequest.get(1.0, END))
        config.saveOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_TYPE, self.entry_characterType.get())
        # config.saveOption(config.SECTION_CHARACTER_REQUESTS_EXTENDED, config.CHARACTER_IMAGE_FORMATS, self.entry_characterImageFormat.get())

        self.is_entry_changed = False

        if (exit_settings):
            self.oWindow.close_window()

    def destroy(self):
        """Destroy Character Requests Settings Panel."""
        if (self.is_entry_changed):
            save_changes = messagebox.askyesno(title="Save Changes?", message="Do you want to save your changes?")
            if (save_changes):
                self.save_settings(exit_settings=False)

        self.is_entry_changed = False
        self.panel.destroy()
        del self

    def entry_edit_how_to_request(self, inStr):
        """Run when entry for how to request is edited.

        Updates label for how to request to match what the user has inputed.
        """
        new_command = self.entry_commandHowToRequest.get()
        self.label_howToRequestText['text'] = new_command
        print(inStr)
        return True


class SmiteApiSettingsPanel(Panel):
    """Smite API Settings Panel."""

    def __init__(self, oWindow):
        print("SmiteAPISettings() init")
        super().__init__(oWindow, row=0, column=1, rowspan=1, columnspan=1)
        self.title = self.oWindow.SMITE_API_SETTINGS

        tk_helper = TkinterHelper(self.panel)
        tk_helper.sticky = "NSWE"
        self.is_feature_smite_api = IntVar()
        self.label_is_feature_smite_api = tk_helper.create_checkbox_grid(text="Enable Feature Smite API", int_var=self.is_feature_smite_api,
                                                                         function=self.toggle_feature)

        tk_helper.next_row()
        self.label_smite_username = tk_helper.create_label_grid("Smite Username:")
        tk_helper.next_column()
        self.entry_smite_username = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        tk_helper.next_row()
        self.label_command_duel_rank = tk_helper.create_label_grid("Duel Rank Command:")
        tk_helper.next_column()
        self.entry_command_duel_rank = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        tk_helper.next_row()
        self.label_command_current_skin = tk_helper.create_label_grid("Current Skin Command:")
        tk_helper.next_column()
        self.entry_command_current_skin = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        tk_helper.next_row()
        self.label_command_time_played = tk_helper.create_label_grid("Time Played Command:")
        tk_helper.next_column()
        self.entry_command_time_played = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        tk_helper.next_row()
        self.label_command_worshippers = tk_helper.create_label_grid("Worshippers Command:")
        tk_helper.next_column()
        self.entry_command_worshippers = tk_helper.create_entry_grid(
            entry_changed_function=self.entry_changed)

        # Save button
        tk_helper.next_row(starting_column=1)
        tk_helper.sticky = 'nswe'
        self.button_save_settings = tk_helper.create_button_grid("Save and Close Settings", function=self.save_settings)
        self.load_settings()

    def load_settings(self):
        """Load Smite API Settings Panel."""
        config = HatBotConfig.HatBotConfig()
        if (config.loadBoolean(config.SECTION_TOGGLED_FEATURES, config.FEATURE_SMITE_API)):
            self.is_feature_smite_api.set(1)
        self.entry_smite_username.insert(0, config.load_option(config.SECTION_SMITE_API, config.SMITE_USERNAME, ""))
        self.entry_command_time_played.insert(0, config.load_option(config.SECTION_SMITE_API, config.COMMAND_TIME_PLAYED, ""))
        self.entry_command_current_skin.insert(0, config.load_option(config.SECTION_SMITE_API, config.COMMAND_CURRENT_SKIN, ""))
        self.entry_command_duel_rank.insert(0, config.load_option(config.SECTION_SMITE_API, config.COMMAND_DUEL_RANK, ""))
        self.entry_command_worshippers.insert(0, config.load_option(config.SECTION_SMITE_API, config.COMMAND_WORSHIPPERS, ""))

        self.is_entry_changed = False

    def save_settings(self, exit_settings=True):
        """Save Smite API Settings Panel."""
        # oConfig.set("Command Names", "", .get())
        # Save command settings
        # oConfig.set("Command Names", "request character", self.entry_commandRequest.get())

        config = HatBotConfig.HatBotConfig()
        config.saveOption(config.SECTION_TOGGLED_FEATURES, config.FEATURE_SMITE_API, self.is_feature_smite_api.get())
        config.saveOption(config.SECTION_SMITE_API, config.SMITE_USERNAME, self.entry_smite_username.get())
        config.saveOption(config.SECTION_SMITE_API, config.COMMAND_DUEL_RANK, self.entry_command_duel_rank.get())
        config.saveOption(config.SECTION_SMITE_API, config.COMMAND_TIME_PLAYED, self.entry_command_time_played.get())
        config.saveOption(config.SECTION_SMITE_API, config.COMMAND_WORSHIPPERS, self.entry_command_worshippers.get())
        config.saveOption(config.SECTION_SMITE_API, config.COMMAND_CURRENT_SKIN, self.entry_command_current_skin.get())
        self.is_entry_changed = False

        if (exit_settings):
            self.oWindow.close_window()

    def destroy(self):
        """Destroy Smite API Settings Panel."""
        if (self.is_entry_changed):
            save_changes = messagebox.askyesno(title="Save Changes?", message="Do you want to save your changes?")
            if (save_changes):
                self.save_settings(exit_settings=False)

        self.panel.destroy()
        self.is_entry_changed = False
        del self

    def toggle_feature(self):
        """Toggle feature for Smite API."""
        print("Toggle Smite API Feature")
        config = HatBotConfig.HatBotConfig()
        config.saveOption(config.SECTION_TOGGLED_FEATURES, config.FEATURE_SMITE_API,
                          str(self.is_feature_smite_api.get()))


def main():
    """Enter Main method."""
    main_window = MainWindow()
    main_window.main_loop()


if __name__ == "__main__":
    main()
