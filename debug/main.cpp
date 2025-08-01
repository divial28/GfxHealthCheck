#include "../lib/src/glxcontext.h"

int main()
{
    createGlxContext(1, 1);
    gladLoadFunctions();
    gladGetMajorVersion();
    gladGetMinorVersion();
    testBasicOpenGlFunctions();
    destroyGlxContext();
    return 0;
}