cmake_minimum_required(VERSION 3.7...3.10)

project(ReX LANGUAGES CXX VERSION 0.0.0)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# which gl loader to use
set(REX_GLLOADER_GLAD OFF)
set(REX_GLLOADER_GLEW ON)

# build additional targets
set(REX_BUILD_TESTS ON)
set(REX_BUILD_TOOLS ON)
set(REX_BUILD_EXAMPLES ON)

# features
# enable use of glGetError, hurts perfomance
set(REX_ENABLE_GL_GET_ERROR ON)

find_package(Qt5 REQUIRED COMPONENTS Core)

file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "src/*.h")
add_library(${PROJECT_NAME} ${SOURCES} ${HEADERS})

target_include_directories(${PROJECT_NAME} PUBLIC include)
target_include_directories(${PROJECT_NAME} PRIVATE src)
target_link_libraries(${PROJECT_NAME} PUBLIC Qt5::Core)

if (MINGW)
    target_link_libraries(${PROJECT_NAME} PRIVATE opengl32)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE GL)
endif()

if(REX_ENABLE_GL_GET_ERROR)
    target_compile_definitions(${PROJECT_NAME} PUBLIC REX_ENABLE_GL_GET_ERROR)
endif()

if(REX_GLLOADER_GLAD)
    target_compile_definitions(${PROJECT_NAME} PUBLIC REX_GLLOADER_GLAD)
    message(FATAL_ERROR "GLAD not supported yet!")
elseif(REX_GLLOADER_GLEW)
    target_compile_definitions(${PROJECT_NAME} PUBLIC REX_GLLOADER_GLEW)
    find_package(GLEW REQUIRED) # TODO: 
    target_include_directories(${PROJECT_NAME} PRIVATE ${GLEW_INCLUDE_DIRS})
    target_link_libraries(${PROJECT_NAME} PRIVATE ${GLEW_LIBRARIES})
else()
    message(FATAL_ERROR "No GL loader specified!")
endif()

if (REX_BUILD_TOOLS)
    add_subdirectory(tools/UI)
endif()

if (REX_BUILD_EXAMPLES)
    add_subdirectory(examples/Sandbox)
endif()

if(REX_BUILD_TESTS)
    enable_testing() # must use here for vscode ctest integration
    add_subdirectory(tests)
endif()
