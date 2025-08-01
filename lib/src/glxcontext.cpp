#include "glxcontext.h"
#include "../glad/glad.h"

#include <GL/gl.h>
#include <GL/glx.h>
#include <X11/Xlib.h>

namespace {
Display*   g_display = nullptr;
Window     g_win;
GLXContext g_context;
} // namespace

int createGlxContext(int w, int h)
{
    g_display = XOpenDisplay(nullptr);
    if (!g_display) {
        return 1;
    }

    static int visualAttribs[] = {GLX_RGBA, GLX_DEPTH_SIZE, 24, GLX_DOUBLEBUFFER, None};

    int          screen = DefaultScreen(g_display);
    XVisualInfo* vi     = glXChooseVisual(g_display, screen, visualAttribs);
    if (!vi) {
        return 2;
    }

    g_context = glXCreateContext(g_display, vi, nullptr, GL_TRUE);
    if (!g_context) {
        return 3;
    }

    Window   root = RootWindow(g_display, vi->screen);
    Colormap cmap = XCreateColormap(g_display, root, vi->visual, AllocNone);

    XSetWindowAttributes swa{};
    swa.colormap   = cmap;
    swa.event_mask = ExposureMask | KeyPressMask;

    g_win = XCreateWindow(g_display, root, 0, 0, w, h, 0, vi->depth, InputOutput, vi->visual, CWColormap | CWEventMask,
                          &swa);

    // XMapWindow(g_display, g_win);
    glXMakeCurrent(g_display, g_win, g_context);
    return 0;
}

int destroyGlxContext()
{
    glXDestroyContext(g_display, g_context);
    XDestroyWindow(g_display, g_win);
    XCloseDisplay(g_display);
    return 0;
}

int gladLoadFunctions() 
{
    return gladLoadGL();
}

int gladGetMajorVersion()
{
    return GLVersion.major;
}

int gladGetMinorVersion()
{
    return GLVersion.minor;
}