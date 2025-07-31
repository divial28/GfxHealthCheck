#include "glxcontext.h"

#include <GL/gl.h>
#include <GL/glx.h>
#include <X11/Xlib.h>

#include <iostream>

int checkContext()
{
    Display* display = XOpenDisplay(nullptr);
    if (!display) {
        std::cerr << "Failed to open X display\n";
        return 1;
    }

    static int visualAttribs[] = {
        GLX_RGBA, GLX_DEPTH_SIZE, 24, GLX_DOUBLEBUFFER, None
    };

    int screen = DefaultScreen(display);
    XVisualInfo* vi = glXChooseVisual(display, screen, visualAttribs);
    if (!vi) {
        std::cerr << "No appropriate visual found\n";
        return 1;
    }

    GLXContext context = glXCreateContext(display, vi, nullptr, GL_TRUE);
    if (!context) {
        std::cerr << "Failed to create GLX context\n";
        return 1;
    }

    Window root = RootWindow(display, vi->screen);
    Colormap cmap = XCreateColormap(display, root, vi->visual, AllocNone);

    XSetWindowAttributes swa{};
    swa.colormap = cmap;
    swa.event_mask = ExposureMask | KeyPressMask;

    Window win = XCreateWindow(display, root, 0, 0, 100, 100, 0,
                               vi->depth, InputOutput, vi->visual,
                               CWColormap | CWEventMask, &swa);

    XMapWindow(display, win);
    glXMakeCurrent(display, win, context);

    const GLubyte* renderer = glGetString(GL_RENDERER);
    const GLubyte* version  = glGetString(GL_VERSION);
    const GLubyte* vendor  = glGetString(GL_VENDOR);

    std::cout << "OpenGL Renderer: " << renderer << "\n";
    std::cout << "OpenGL Version: " << version << "\n";
    std::cout << "OpenGL Vendor: " << vendor << "\n";

    glXDestroyContext(display, context);
    XDestroyWindow(display, win);
    XCloseDisplay(display);
    return 0;
}