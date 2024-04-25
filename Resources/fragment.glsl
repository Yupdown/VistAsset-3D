#version 460 core

uniform sampler2D main_Texture;

uniform vec3 light_Position;
uniform vec3 view_Position;

uniform vec3 ambient_Color;
uniform vec3 diffuse_Color;
uniform vec3 specular_Color;

in vec3 vert_Position;
in vec3 vert_Normal;
in vec4 vert_Color;
in vec2 vert_UV;

out vec4 out_Color;

void main()
{
	out_Color = vert_Color;
}