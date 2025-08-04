cmake_minimum_required(VERSION 3.7...3.10)

project(GfxHealthCheck LANGUAGES C CXX VERSION 0.0.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

set(GHC_BUILD_DEBUG OFF)

add_subdirectory(lib)

if(GHC_BUILD_DEBUG)
    add_subdirectory(debug)
endif()
