#version 460 core

uniform sampler2D main_Texture;

in vec3 vert_Position;
in vec3 vert_Normal;
in vec4 vert_Color;
in vec2 vert_UV;

out vec4 out_Color;

void main()
{
    vec3 light_Dir = normalize(vec3(0.0, 1.0, 1.0));
    vec3 normal = normalize(vert_Normal);
    float diff = max(dot(normal, light_Dir), 0.0);
    vec3 reflect_Dir = reflect(-light_Dir, normal);
    vec3 view_Dir = normalize(vec3(0.0, 0.0, 1.0));
    float spec = pow(max(dot(view_Dir, reflect_Dir), 0.0), 32.0);
    vec3 ambient = vec3(0.1, 0.1, 0.1);
    vec3 diffuse = vec3(0.8, 0.8, 0.8) * diff;
    vec3 specular = vec3(1.0, 1.0, 1.0) * spec;

    out_Color = vec4(ambient + diffuse + specular, 1.0) * vert_Color;
}