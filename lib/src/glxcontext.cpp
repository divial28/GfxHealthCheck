#include "glxcontext.h"
#include "../glad/glad.h"

#include <cstdio>
#include <string>

#include <GL/gl.h>
#include <GL/glx.h>
#include <X11/Xlib.h>

namespace {

Display*   g_display = nullptr;
Window     g_win;
GLXContext g_context;

const char* glErrorStr(GLenum err)
{
#define CASE(x)                                                                                                        \
    case x:                                                                                                            \
        return #x
    switch (err) {
        CASE(GL_NO_ERROR);
        CASE(GL_INVALID_ENUM);
        CASE(GL_INVALID_VALUE);
        CASE(GL_INVALID_OPERATION);
        CASE(GL_INVALID_FRAMEBUFFER_OPERATION);
        CASE(GL_OUT_OF_MEMORY);
        CASE(GL_STACK_UNDERFLOW);
        CASE(GL_STACK_OVERFLOW);
    }
    return "UNKNOWN_ERROR";
}

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
    g_win     = 0;
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

int gladGetMajorVersion() { return GLVersion.major; }

int gladGetMinorVersion() { return GLVersion.minor; }

Result getOpenGLVersionString()
{
    return {0, (char*)glGetString(GL_VERSION)};
}

#define GL_CHECK(stmt)                                                                                                 \
    do {                                                                                                               \
        stmt;                                                                                                          \
        GLenum err = glGetError();                                                                                     \
        if (err != GL_NO_ERROR) {                                                                                      \
            output += std::string(#stmt " : ") + glErrorStr(err) + "|";                                              \
        }                                                                                                              \
    } while (0)

Result testBasicOpenGlFunctions()
{
    static std::string   output;
    static const GLchar* vsSource = R"glsl(
        #version 430 core
        layout(location = 0) in vec2 aPos;
        void main() {
            gl_Position = vec4(aPos, 0.0, 1.0);
        }
    )glsl";
    static const GLchar* fsSource = R"glsl(
        #version 430 core
        out vec4 FragColor;
        void main() {
            FragColor = vec4(1.0, 0.5, 0.2, 1.0);
        }
    )glsl";
    GLuint               vao = 0, vbo = 0, ebo = 0, shader = 0, vs = 0, fs = 0;
    GLfloat              vertices[] = {-0.5, -0.5, 0.0, 0.5, 0.5, -0.5};
    GLuint               indices[]  = {0, 1, 2};
    GLint                success;
    GLchar               log[512];

    output = {};

    GL_CHECK(glGenVertexArrays(1, &vbo));
    GL_CHECK(glGenBuffers(1, &vbo));
    GL_CHECK(glGenBuffers(1, &ebo));
    GL_CHECK(glBindVertexArray(vao));
    GL_CHECK(glBindBuffer(GL_ARRAY_BUFFER, vbo));
    GL_CHECK(glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), nullptr, GL_STATIC_DRAW));
    GL_CHECK(glBufferSubData(GL_ARRAY_BUFFER, 0, sizeof(vertices), vertices));
    GL_CHECK(glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo));
    GL_CHECK(glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(indices), nullptr, GL_STATIC_DRAW));
    GL_CHECK(glBufferSubData(GL_ELEMENT_ARRAY_BUFFER, 0, sizeof(indices), indices));
    GL_CHECK(glEnableVertexAttribArray(0));
    GL_CHECK(glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, 0));
    GL_CHECK(vs = glCreateShader(GL_VERTEX_SHADER));
    GL_CHECK(glShaderSource(vs, 1, &vsSource, nullptr));
    GL_CHECK(glCompileShader(vs));
    GL_CHECK(glGetShaderiv(vs, GL_COMPILE_STATUS, &success));
    if (!success) {
        GL_CHECK(glGetShaderInfoLog(vs, 512, nullptr, log));
        output += std::string("Vertex Shader Compilation Error:\n") + log + "|";
    }
    GL_CHECK(fs = glCreateShader(GL_FRAGMENT_SHADER));
    GL_CHECK(glShaderSource(fs, 1, &fsSource, nullptr));
    GL_CHECK(glCompileShader(fs));
    GL_CHECK(glGetShaderiv(fs, GL_COMPILE_STATUS, &success));
    if (!success) {
        GL_CHECK(glGetShaderInfoLog(fs, 512, nullptr, log));
        output += std::string("Fragment Shader Compilation Error:\n") + log + "|";
    }
    GL_CHECK(shader = glCreateProgram());
    GL_CHECK(glAttachShader(shader, vs));
    GL_CHECK(glAttachShader(shader, fs));
    GL_CHECK(glLinkProgram(shader));
    GL_CHECK(glGetProgramiv(shader, GL_LINK_STATUS, &success));
    if (!success) {
        GL_CHECK(glGetShaderInfoLog(shader, 512, nullptr, log));
        output += std::string("Shader Program Linking Error:\n") + log + "|";
    }
    GL_CHECK(glUseProgram(shader));
    GL_CHECK(glDeleteShader(vs));
    GL_CHECK(glDeleteShader(fs));
    GL_CHECK(glClearColor(1.0f, 1.0f, 1.0f, 1.0f));
    GL_CHECK(glClear(GL_COLOR_BUFFER_BIT));
    GL_CHECK(glDrawArrays(GL_TRIANGLES, 0, 3));
    GL_CHECK(glDrawElements(GL_TRIANGLES, 0, GL_UNSIGNED_INT, (void*)3));
    GL_CHECK(glFlush());
    GL_CHECK(glUseProgram(0));
    GL_CHECK(glDisableVertexAttribArray(0));
    GL_CHECK(glBindVertexArray(0));
    GL_CHECK(glBindBuffer(GL_ARRAY_BUFFER, 0));
    GL_CHECK(glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0));
    GL_CHECK(glDeleteProgram(shader));
    GL_CHECK(glDeleteVertexArrays(1, &vao));
    GL_CHECK(glDeleteBuffers(1, &vbo));
    GL_CHECK(glDeleteBuffers(1, &ebo));

    if (output.empty()) {
        return {0, ""};
    }

    output.erase(output.size() - 1);
    return {1, output.c_str()};
}