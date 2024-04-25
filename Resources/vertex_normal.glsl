#version 460 core

layout(location = 0) in vec3 in_Position;
layout(location = 1) in vec3 in_Normal;
layout(location = 2) in vec3 in_Color;
layout(location = 3) in vec2 in_UV;

layout(std140, binding = 0) uniform GlobalUniform
{
	mat4 view_Transform;
	mat4 proj_Transform;
};

uniform mat4 model_Transform;

out vec3 vert_Position;
out vec3 vert_Normal;
out vec4 vert_Color;
out vec2 vert_UV;

void main()
{
	vert_Position = vec3(model_Transform * vec4(in_Position, 1.0));
	gl_Position = proj_Transform * view_Transform * vec4(vert_Position, 1.0);
	vert_Color = vec4(in_Normal * 0.5 + 0.5, 1.0);
}