from pyglet.gl import * # pylint: disable=W0614


class LetterboxViewport:
    # Some GL-specific code is commented out. This means that for now everything works without it, but may be needed
    # if something changes later

    def __init__(self, window: pyglet.window.Window, scene_width: int, scene_height: int, smooth_scaling: bool = False):
        self.window = window
        self.scene_width = scene_width
        self.scene_height = scene_height
        self.texture = pyglet.image.Texture.create(scene_width, scene_height,
                                                   rectangle=scene_width != scene_height)

        if not smooth_scaling:
            # Disable smooth scaling
            glTexParameteri(self.texture.target, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(self.texture.target, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glClearColor(0, 0, 0, 1)
        glMatrixMode(GL_PROJECTION)

        self.texture_x = self.texture_y = self.scale_width = self.scale_height = 0

        @window.event
        def on_resize(w, h):
            self.on_window_resize()
        self.on_window_resize()

        self._context_manager = self.ContextManager(self)

    def begin_drawing(self):
        glViewport(0, 0, self.scene_width, self.scene_height)
        self.set_fixed_projection()
        glClear(GL_COLOR_BUFFER_BIT)

    def end_drawing(self):
        buffer = pyglet.image.get_buffer_manager().get_color_buffer()
        self.texture.blit_into(buffer, 0, 0, 0)

        glViewport(0, 0, self.window.width, self.window.height)
        self.set_window_projection()

        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 1, 1)

        self.texture.blit(self.texture_x, self.texture_y, width=self.scale_width, height=self.scale_height)
        self.on_window_resize()

    def draw(self) -> 'LetterboxViewport.ContextManager':
        return self._context_manager

    def set_fixed_projection(self) -> None:
        # Override this method if you need to change the projection of the fixed resolution viewport.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.scene_width, 0, self.scene_height, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def set_window_projection(self) -> None:
        # This is the same as the default window projection, reprinted here for clarity.
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.window.width, 0, self.window.height, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def on_window_resize(self) -> None:
        scale = min(self.window.width / self.scene_width, self.window.height / self.scene_height)
        self.scale_width = scale * self.scene_width
        self.scale_height = scale * self.scene_height

        self.texture_x = (self.window.width - self.scale_width) / 2
        self.texture_y = (self.window.height - self.scale_height) / 2

    class ContextManager:
        """Internal context manager representation of LetterboxViewport"""
        def __init__(self, master: 'LetterboxViewport'):
            self.master = master

        def __enter__(self):
            self.master.begin_drawing()

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.master.end_drawing()
