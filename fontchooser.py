"""
Font dialog for Python based on tk fontchooser.

*** Work-in-progress ***

The underlying dialog is deceptively messy and its behaviour varies across platforms.
Factor in additional bugs on various platforms, and the benefits of a wrapper that hides
at least some of the ugly details and differences becomes clear.

Thie file impleements the Chooser class which provides the dialog.

For now, there are also two demos illustrating its use:

  - FontChooserSimpleDemo is about as barebones as it gets

  - FontChooserDemo is more involved but shows what a real application would often
    need to do, adjusting the interface to take into account whether the dialog is 
    modal or not, currently visible or not, and adjusting the dialog as focus moves 
    between different text widgets, etc.

You can comment out one or the other at the bottom of the file.

For reference, I've included below my notes on how the underlying dialog works on different
platforms, warts and all. Not as simple as it perhaps should be!

From the manual:
 - configure -font is the font currently shown or font shown when dialog is initially shown (neither guaranteed on all platforms)
 - implementation-dependent which actions result in callback being called and event being sent

Windows
 - modal; show blocks until dismissed, user cannot interact with other windows
 - dialog callbacks and event handlers in your code are called while dialog is onscreen, so your code can manipulate other windows
 - ok/cancel
 - apply button added if a command option is specified
 - with command (apply button present)
    - if apply: callback generated with font currently set in dialog, event generated [configure -font is NOT updated]
    - if ok: callback generated with font in dialog, dialog closed, event generated, configure -font not updated
 - if no command (no apply button)
    - on ok, get event, configure -font not updated (ok, since dialog not visible, though not helpful...)
 - fontchange event not generated if option is set in code

X11
 - not modal; show returns immediately, can interact with other windows
 - ok/cancel
 - apply button added if a command option is specified
 - with command (apply button present):
    - if apply: callback generated with font currently set in dialog, event generated [configure -font is NOT updated)
    - if ok: callback generated with font in dialog, dialog closed; no event, configure -font NOT updated (should be; see BUG below)
 - with no command (no apply button):
    - no event generated, configure -font NOT updated
 - fontchnaged event generated if option is set in code, configure -font updated
 - configure -font never updated by user interaction (is updated on OK with workaround for BUG below)
 - conclusion: always set command, hold onto current value returned (latter not needed if BUG, below, is fixed)
 - BUG: specifying subset of options on tk fontchooser configure overwrites those not specified
    - bug filed: https://core.tcl-lang.org/tk/tktview?name=4ebcc04dc4

macOS
 - no ok/cancel buttons, works like a palette
 - non-modal; show returns immediately, can interact with other windows
 - BUG:can appear when tk first loaded (sometimes..)
 - happens when left open on previous launches and program exited abnormally e.g. ctl-C in terminal
 - ~/Library/Saved Application State/com.tcltk.wish.savedState/windows.plist still holds font chooser
 - if so, -visible initially is false, but is true after idle... no intervening <<TkFontChooserVisibility>> event
 - will segfault if set options e.g. font
 - bug filed: https://core.tcl-lang.org/tk/tktview?name=c2483bfe4b
 - workaround: hide on startup
 - fontchange event generated on every change in dialog, configure -font updated to font in dialog
 - fontchange event generated when option set in code, configure -font updated to font in dialog
 - command callback (if specified) invoked on every change from user (not in code), configure -font updated
 - if not given an initial font, will never invoke callback; see bug: https://core.tcl-lang.org/tk/tktview/4f84af7b4cd5df34189a

"""


import tkinter
from tkinter.font import Font


class Chooser:

    """
    Wrapper for "tk fontchooser" dialog available starting in Tk 8.6.
    
    Available options for contructor (or configure):
        parent      Logical parent window we're providing the font chooser for
        title       Dialog title (ignored on macOS)
        font        Font to start dialog on next time
                      - format can vary (empty string, font specification string, named font, tkinter.Font object)
                      - updated on macOS on all font changes, on X11 and Windows when dialog dismissed with "OK"
        command     Callback for when font is changed; accepts one parameter, a tkinter.Font object

    
    Public methods:
        configure(...)  Examine or change dialog options; akin to configure() method on widgets;
    
        show()          Display dialog; may or may not return immediately; see ismodal()
    
        hide()          If font dialog is visible, hide it; not needed for modal dialogs
    
        isvisible()     True if font dialog is currently onscreen (use this instead of -visible configuration option)
    
        ismodal()       True if dialog is modal on this platform (convenience method not in Tk API)

        mayhavefocus()  True if font dialog might currently have the keyboard focus on this platform (convenience method not in Tk API)
                        Always False on macOS, True on Windows and X11 if font dialog is visible.
    

    The following virtual events are generated on the parent window:
        <<TkFontchooserVisibility>>     When dialog is shown or hidden (fairly reliably...)
        <<TkFontchooserFontChanged>>    When font is changed in dialog or in code (sometimes)


    Notable differences from underlying Tk API:
    
    1. Use isvisible() method instead of read-only '-visible' configuration option.
    2. Convenience methods ismodal() and mayhavefocus() which allow client code to determine platform behaviour.
    3. We always specify a -command option to Tk (even if the Python callback is not specified).
       That means on Windows and X11, the font dialog always has an Apply button (as well as OK/Cancel).
    4. On Windows, the -font option is updated when the dialog is dismissed by the user pressing OK.
    5. Workaround for bug on macOS where fontchooser could start open based on saved application state.
    6. Workaround for bug on macOS where fontchooser needs an initial font set before will invoke callbacks.
    7. Workaround for bug on X11 where using configure with a subset of option would reset others to default.


    Still to be fixed:
    
    - configure should translate Tcl option lists into Python format, remove all trace of -visible option
    - are conditional statements (e.g., in FontChooserDemo.toggle) kosher?
    - cleaner way to set all options (in Chooser.__setitem__)
    - line lengths

    """
    
    def __init__(self, **kw):
        self._command = None
        self.w = kw.get('parent') if kw.get('parent') else tkinter._default_root
        self.w.tk.call('tk', 'fontchooser', 'configure', '-command', self.w.register(self._font_changed))
        self.configure(**kw)
        if self.w._windowingsystem == 'aqua':
            self.w.after(1, self.hide)   # workaround startup bug on macOS
            self.w.tk.call('tk', 'fontchooser', 'configure', '-font', 'TkDefaultFont')

    def hide(self):
        """Hide the font selection dialog if visible."""
        self.w.tk.call("tk", "fontchooser", "hide")

    def show(self):
        """Show the font selection dialog. This method does not return a value. On platforms where the 
           font chooser is modal, this method won't return until the font chooser is dismissed. On other
           platforms, this method returns immediately."""
        self.w.tk.call("tk", "fontchooser", "show")

    def configure(self, **options):
        """Set the values of one or more options."""
        for k in options:
          self[k] = options[k]
          
    config = configure

    def _font_changed(self, fontspec):
        """Callback from fontchooser when font is changed"""
         # On Windows, update -font if OK pressed in modal dialog, but not if Apply pressed
        if self.ismodal() and not self.isvisible():
            self['font'] = fontspec
        if self._command:
            self._command(Font(font=fontspec))
        
    def ismodal(self):
        """True if font chooser is modal on this platform"""
        return self.w._windowingsystem == "win32"
        
    def mayhavefocus(self):
        """True if font chooser might have focus on this platform"""
        return (self.w._windowingsystem in ["x11", "win32"]) and self.isvisible()

    def isvisible(self):
        return self.w.tk.call('tk', 'fontchooser', 'configure', '-visible') == 1
        
    def __setitem__(self, key, value):
        if key == "command":
            self._command = value
        else:
            # workaround bug on X11 where all options need to be specified, or those not specified are reset to defaults
            command = self.w.tk.call('tk', 'fontchooser', 'configure', '-command')
            parent = value if key=='parent' else self.w.tk.call('tk', 'fontchooser', 'configure', '-parent')
            title = value if key=='title' else self.w.tk.call('tk', 'fontchooser', 'configure', '-title')
            font = value if key=='font' else self.w.tk.call('tk', 'fontchooser', 'configure', '-font')
            self.w.tk.call("tk", "fontchooser", "configure", "-command", command, "-parent", parent, "-title", title, "-font", font)

    def __getitem__(self, key):
        return self._command if key=="command" else self.w.tk.call("tk", "fontchooser", "configure", "-" + key)
        


if __name__ == "__main__":

    class FontChooserSimpleDemo():
        def __init__(self, w):
            self.w = w
            self.chooser = Chooser(command=self.myfont_changed, parent=self.w)
            self.t = tkinter.Text(self.w, width=20, height=4, borderwidth=1, relief='solid')
            self.t.insert('end', 'testing')
            self.t.grid()
            self.b = tkinter.Button(w, text="Font", command=self.toggle)
            self.b.grid()
            
        def toggle(self):
            self.chooser.hide() if self.chooser.isvisible() else self.chooser.show()

        def myfont_changed(self, font):
            self.t['font'] = font


    class FontChooserDemo():
        def __init__(self, w):
            self.w = w
            self.w.title("Font Chooser Demo")
            self.chooser = Chooser(command=self.font_changed, parent=self.w)
            self.target = None  # Widget we manage currently holding the keyboard focus
            
            # Button to Show/Hide font dialog; label is updated as chooser opens/closes;
            # For platforms where the font dialog is modal, an option in the user interface to hide it
            # doesn't make sense (you'd never be able to use it). In that case, the button always says "Font...".
            self.fc_btn = tkinter.Button(w, takefocus=0, command=self.toggle)
            self.fc_btn.grid()
            self.w.bind('<<TkFontchooserVisibility>>', self.visibility_changed)
            self.w.bind('<<TkFontchooserFontChanged>>', self.font_changed_event)
            if self.chooser.ismodal():
                self.fc_btn['text'] = 'Font...'
                self.fc_btn['state'] = 'disabled'
            else:
                self.visibility_changed()
            
            # two text widgets which respond to font changes
            self.create_fontable_text(('Courier', 12)).grid()
            self.create_fontable_text(('Helvetica', 14, 'bold')).grid()
            
            # text widget that doesn't respond to font changes
            t = tkinter.Text(self.w, width=20, height=4, borderwidth=1, relief='solid')
            t.insert('end', 'not changed by font chooser')
            t.grid()
            
        def visibility_changed(self, *args):
            """Respond to font dialog being shown or hidden."""
            if not self.chooser.ismodal():
                self.fc_btn['text'] = 'Hide Fonts' if self.chooser.isvisible() else 'Show Fonts'

        def toggle(self):
            """Show/Hide font dialog"""
            self.chooser.hide() if self.chooser.isvisible() else self.chooser.show()

        def create_fontable_text(self, font):
            """Simple text widget that allows font changes via font chooser."""
            t = tkinter.Text(self.w, width=20, height=4, borderwidth=1, relief='solid', font=font)
            t.insert('end', 'testing')
            t.bind('<FocusIn>', lambda ev: self.gained_focus(t))
            t.bind('<FocusOut>', lambda ev: self.lost_focus(t))
            return t
            
        def gained_focus(self, w):
            """One of our text widgets gained focus. Update the font chooser to match its current font"""
            self.chooser['font'] = w['font']
            self.target = w
            self.fc_btn['state'] = 'normal'
            
        def lost_focus(self, w):
            """One of our text widgets lost focus. It will no longer be the target of future font changes."""
            if not self.chooser.mayhavefocus():
                # Ideally, if we move the keyboard focus elsewhere, the font dialog shouldn't update one
                # of our fontable_text widgets. That doesn't work so well if the font dialog will steal 
                # the focus...
                self.target = None
            if self.chooser.ismodal():
                self.fc_btn['state'] = 'disabled'

        def font_changed(self, font):
            """Callback when font is changed, update target text widget"""
            if self.target:
                self.target['font'] = font

        def font_changed_event(self, *args):
            """<<TkFontchooserFontChanged>> event generated; not used."""
            pass

                
    root = tkinter.Tk()
    # FontChooserSimpleDemo(root)
    FontChooserDemo(root)
    root.mainloop()

