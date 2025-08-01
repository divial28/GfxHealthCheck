#include "glxcontext.h"
#include "../glad/glad.h"

#include <string>

#include <GL/gl.h>
#include <GL/glx.h>
#include <X11/Xlib.h>

namespace {
Display*   g_display = nullptr;
Window     g_win;
GLXContext g_context;
} // namespace

Result createGlxContext(int w, int h)
{
    g_display = XOpenDisplay(nullptr);
    if (!g_display) {
        return {1, "GLX failed to open X display"};
    }

    static int visualAttribs[] = {GLX_RGBA, GLX_DEPTH_SIZE, 24, GLX_DOUBLEBUFFER, None};

    int          screen = DefaultScreen(g_display);
    XVisualInfo* vi     = glXChooseVisual(g_display, screen, visualAttribs);
    if (!vi) {
        XCloseDisplay(g_display);
        g_display = nullptr;
        return {2, "GLX couldn't find appropriate visual"};
    }

    g_context = glXCreateContext(g_display, vi, nullptr, GL_TRUE);
    if (!g_context) {
        XFree(vi);
        XCloseDisplay(g_display);
        g_display = nullptr;
        return {3, "GLX failed to create OpenGL context"};
    }

    Window   root = RootWindow(g_display, vi->screen);
    Colormap cmap = XCreateColormap(g_display, root, vi->visual, AllocNone);

    XSetWindowAttributes swa{};
    swa.colormap   = cmap;
    swa.event_mask = ExposureMask | KeyPressMask;

    g_win = XCreateWindow(g_display, root, 0, 0, w, h, 0, vi->depth, InputOutput, vi->visual, CWColormap | CWEventMask,
                          &swa);
    if (!g_win) {
        glXDestroyContext(g_display, g_context);
        g_context = nullptr;
        XFreeColormap(g_display, cmap);
        XFree(vi);
        XCloseDisplay(g_display);
        g_display = nullptr;
        return {4, "GLX failed to create window"};
    }

    // XMapWindow(g_display, g_win);
    if (!glXMakeCurrent(g_display, g_win, g_context)) {
        glXDestroyContext(g_display, g_context);
        g_context = nullptr;
        XDestroyWindow(g_display, g_win);
        g_win = 0;
        XFreeColormap(g_display, cmap);
        XFree(vi);
        XCloseDisplay(g_display);
        g_display = nullptr;
        return {5, "GLX failed to make context current"};
    }

    XFree(vi);
    return {0, ""};
}

Result destroyGlxContext()
{
    glXMakeCurrent(g_display, 0, 0);
    glXDestroyContext(g_display, g_context);
    XDestroyWindow(g_display, g_win);
    XCloseDisplay(g_display);
    g_context = nullptr;
    g_win = 0;
    g_display = nullptr;
    return {0, ""};
}

Result gladLoadFunctions() 
{
    if (gladLoadGL()) {
        return {0, ""};
    }
    return {1, "GLX failed to load OpenGL functions"};
}

int gladGetMajorVersion()
{
    return GLVersion.major;
}

int gladGetMinorVersion()
{
    return GLVersion.minor;
}

Result testBasicOpenGlFunctions()
{
    static std::string output;

    

    return {0, output.c_str()};
}