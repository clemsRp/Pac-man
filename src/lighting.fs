#version 330 core
in vec2 fragTexCoord;
in vec4 fragColor;

uniform sampler2D texture0;
uniform vec2 mazeSize;
uniform vec2 lightPos;
uniform float radius;
uniform vec3 lightColor;

out vec4 finalColor;

void main()
{
    vec2 posInMaze = fragTexCoord * mazeSize;
    vec2 dir = lightPos - posInMaze;
    float dist = length(dir);
    
    if (dist > radius) {
        finalColor = vec4(0.0, 0.0, 0.0, 1.0);
        return;
    }
    
    vec2 stepSize = dir / max(1.0, dist);
    float shadow = 1.0;
    
    for(int i = 2; i < int(dist); i++) {
        vec2 samplePos = posInMaze + stepSize * float(i);
        vec2 sampleTexCoord = samplePos / mazeSize;
        
        float wall = texture(texture0, sampleTexCoord).r;
        if (wall > 0.5) {
            shadow = 0.0;
            break;
        }
    }
    
    float attenuation = max(0.0, 1.0 - (dist / radius));
    finalColor = vec4(lightColor * attenuation * shadow, 1.0);
}
