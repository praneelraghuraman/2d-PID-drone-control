import pygame
import math

vec2 = pygame.math.Vector2


def get_angle(vec):
    if vec.length() == 0:
        return 0
    return math.degrees(math.atan2(vec.y, vec.x))


def degrees_to_radians(angle):
    return angle / (180 / math.pi)


def radians_to_degrees(rads):
    return rads * 180 / math.pi


def box_line_collided(box, line):
    # check if any of the lines of the box collide with the line
    for i in range(len(box)):
        if lines_collided(
            box[i][0],
            box[i][1],
            box[(i + 1) % len(box)][0],
            box[(i + 1) % len(box)][1],
            line[0],
            line[1],
            line[2],
            line[3],
        ):
            return True
    return False


def lines_collided(x1, y1, x2, y2, x3, y3, x4, y4):
    denominator = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)

    if denominator == 0:
        return lines_collinear(x1, y1, x2, y2, x3, y3, x4, y4)

    uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denominator
    uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denominator

    if 0 <= uA <= 1 and 0 <= uB <= 1:
        return True

    return False


def lines_collinear(x1, y1, x2, y2, x3, y3, x4, y4):
    # Check if the lines have the same slope (parallel)
    slope1 = (
        (y2 - y1) / (x2 - x1) if x2 - x1 != 0 else float("inf")
    )  # Handle vertical line
    slope2 = (
        (y4 - y3) / (x4 - x3) if x4 - x3 != 0 else float("inf")
    )  # Handle vertical line

    if slope1 == slope2:
        # Check if they share a common point, which indicates collinearity
        if (x1, y1) == (x3, y3) or (x1, y1) == (x4, y4):
            return True
        if (x2, y2) == (x3, y3) or (x2, y2) == (x4, y4):
            return True

    return False


def get_collision_point(x1, y1, x2, y2, x3, y3, x4, y4):
    global vec2
    uA = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / (
        (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    )
    uB = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / (
        (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
    )
    if 0 <= uA <= 1 and 0 <= uB <= 1:
        intersectionX = x1 + (uA * (x2 - x1))
        intersectionY = y1 + (uA * (y2 - y1))
        return vec2(intersectionX, intersectionY)
    return None


def rotate_point(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.

    modified from answer here: https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]


def dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def blit_rotate(surf, image, pos, originPos, angle):
    # offset from pivot to center
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center

    # roatated offset from pivot to center
    rotated_offset = offset_center_to_pivot.rotate(-angle)

    # rotated image center
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)

    # rotate and blit the image
    surf.blit(rotated_image, rotated_image_rect)

    # draw rectangle around the image
    # pygame.draw.rect(
    #     surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()), 2
    # )


def draw_arrow(
    surface: pygame.Surface,
    start: pygame.Vector2,
    end: pygame.Vector2,
    color: pygame.Color,
    body_width: int = 2,
    head_width: int = 4,
    head_height: int = 2,
):
    """Draw an arrow between start and end with the arrow head at the end.

    Args:
        surface (pygame.Surface): The surface to draw on
        start (pygame.Vector2): Start position
        end (pygame.Vector2): End position
        color (pygame.Color): Color of the arrow
        body_width (int, optional): Defaults to 2.
        head_width (int, optional): Defaults to 4.
        head_height (float, optional): Defaults to 2.
    """
    arrow = start - end
    angle = arrow.angle_to(pygame.Vector2(0, -1))
    body_length = arrow.length() - head_height

    # Create the triangle head around the origin
    head_verts = [
        pygame.Vector2(0, head_height / 2),  # Center
        pygame.Vector2(head_width / 2, -head_height / 2),  # Bottomright
        pygame.Vector2(-head_width / 2, -head_height / 2),  # Bottomleft
    ]
    # Rotate and translate the head into place
    translation = pygame.Vector2(0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start

    pygame.draw.polygon(surface, color, head_verts)

    # Stop weird shapes when the arrow is shorter than arrow head
    if arrow.length() >= head_height:
        # Calculate the body rect, rotate and translate into place
        body_verts = [
            pygame.Vector2(-body_width / 2, body_length / 2),  # Topleft
            pygame.Vector2(body_width / 2, body_length / 2),  # Topright
            pygame.Vector2(body_width / 2, -body_length / 2),  # Bottomright
            pygame.Vector2(-body_width / 2, -body_length / 2),  # Bottomleft
        ]
        translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
        for i in range(len(body_verts)):
            body_verts[i].rotate_ip(-angle)
            body_verts[i] += translation
            body_verts[i] += start

        pygame.draw.polygon(surface, color, body_verts)
