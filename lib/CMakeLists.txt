cmake_minimum_required(VERSION 3.7...3.10)

# find_package(Qt5 REQUIRED COMPONENTS Core)

file(GLOB_RECURSE SOURCES src/*)
file(GLOB_RECURSE GLAD_SOURCES glad/*)
add_library(${PROJECT_NAME} SHARED
    ${SOURCES}
    ${GLAD_SOURCES}
)

set_target_properties(${PROJECT_NAME} PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/bin
)

# target_link_libraries(${PROJECT_NAME} PUBLIC Qt5::Core)

if (MINGW)
    target_link_libraries(${PROJECT_NAME} PRIVATE opengl32)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE GL)
endif()
