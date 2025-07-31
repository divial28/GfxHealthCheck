cmake_minimum_required(VERSION 3.7...3.10)

# find_package(Qt5 REQUIRED COMPONENTS Core)

file(GLOB_RECURSE SOURCES "src/*.cpp")
file(GLOB_RECURSE HEADERS "src/*.h")
file(GLOB_RECURSE GLAD_SOURCES "src/*.c")
file(GLOB_RECURSE GLAD_HEADERS "src/*.h")
add_library(${PROJECT_NAME} SHARED ${SOURCES} ${HEADERS})

set_target_properties(${PROJECT_NAME} PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin
)

# target_include_directories(${PROJECT_NAME} PRIVATE include)
# target_include_directories(${PROJECT_NAME} PRIVATE src)
# target_link_libraries(${PROJECT_NAME} PUBLIC Qt5::Core)

if (MINGW)
    target_link_libraries(${PROJECT_NAME} PRIVATE opengl32)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE GL)
endif()
