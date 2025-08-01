#pragma once

extern "C" {

struct Result {
    int code;
    const char* message;
};

Result createGlxContext(int w, int h);
Result destroyGlxContext();

Result gladLoadFunctions();
int gladGetMajorVersion();
int gladGetMinorVersion();

Result testBasicOpenGlFunctions();

}