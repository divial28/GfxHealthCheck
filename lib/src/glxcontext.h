#pragma once

#ifdef __cplusplus
extern "C" {
#endif

int createGlxContext(int w, int h);
int destroyGlxContext();

int gladLoadFunctions();
int gladGetMajorVersion();
int gladGetMinorVersion();

#ifdef __cplusplus
}
#endif