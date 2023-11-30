import cv2
import pygame
from pygame.locals import *
from PIL import Image
import os
import random

# Initialize Pygame
pygame.init()

# Set up Pygame window
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Facial Recognition Puzzle Game")

# Function to capture facial image using OpenCV
def capture_face():
    capture = cv2.VideoCapture(0)  # Use the default camera (change if needed)
    
    while True:
        ret, frame = capture.read()
        if not ret:
            print("Failed to capture image.")
            break

        # Display the video feed
        cv2.imshow("Capture Face", frame)

        # Press 'q' to capture the face
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite("captured_face.jpg", frame)
            break

    capture.release()
    cv2.destroyAllWindows()

# Function to display the captured facial image in Pygame window
def display_face(image_path):
    image = pygame.image.load(image_path)
    screen.blit(image, (0, 0))
    pygame.display.flip()

# Function to divide the image into puzzle pieces
def generate_puzzle_pieces(image_path, rows, cols):
    image = Image.open(image_path)
    width, height = image.size
    piece_width = width // cols
    piece_height = height // rows

    pieces = []
    for i in range(rows):
        for j in range(cols):
            left = j * piece_width
            upper = i * piece_height
            right = left + piece_width
            lower = upper + piece_height

            piece = image.crop((left, upper, right, lower))
            pieces.append(piece)

    return pieces

# Function to load puzzle pieces and their rect objects
def load_pieces():
    pieces = []
    piece_rects = []

    puzzle_pieces_folder = "puzzle_pieces"

    # Create the "puzzle_pieces" directory if it doesn't exist
    if not os.path.exists(puzzle_pieces_folder):
        os.makedirs(puzzle_pieces_folder)

    for i, filename in enumerate(os.listdir(puzzle_pieces_folder)):
        piece_path = os.path.join(puzzle_pieces_folder, filename)
        piece = pygame.image.load(piece_path)
        pieces.append(piece)

        # Create rect objects for each piece
        rect = piece.get_rect()
        rect.topleft = (random.randint(50, width - 50), random.randint(50, height - 50))  # Random initial position
        piece_rects.append(rect)

    return pieces, piece_rects

# Function to check if the puzzle pieces are correctly snapped
def check_puzzle_complete(piece_rects, original_rects, tolerance=10):
    for rect, original_rect in zip(piece_rects, original_rects):
        if abs(rect.x - original_rect.x) > tolerance or abs(rect.y - original_rect.y) > tolerance:
            return False
    return True

# Main game loop
def main():
    capture_face()  # Capture the facial image
    face_pieces = generate_puzzle_pieces("captured_face.jpg", rows=4, cols=4)  # Divide the image into puzzle pieces

    # Shuffle the puzzle pieces
    random.shuffle(face_pieces)

    # Display the shuffled puzzle pieces
    for i, piece in enumerate(face_pieces):
        piece_path = f"puzzle_pieces/piece_{i}.png"
        piece.save(piece_path)
        pygame.time.wait(500)  # Pause for a short time between displaying pieces

    # Load puzzle pieces and their rect objects
    original_pieces, original_rects = load_pieces()
    pieces, piece_rects = load_pieces()

    running = True
    dragging = False
    selected_piece = None
    offset_x, offset_y = 0, 0

    moves = 0
    congrats_displayed = False

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    for i, rect in enumerate(piece_rects):
                        if rect.collidepoint(event.pos):
                            selected_piece = i
                            offset_x = rect.x - event.pos[0]
                            offset_y = rect.y - event.pos[1]
                            dragging = True

            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    dragging = False

                    # Check if the puzzle is complete
                    if check_puzzle_complete(piece_rects, original_rects):
                        congrats_displayed = True
                        print("Congratulations! Puzzle completed.")

            elif event.type == MOUSEMOTION:
                if dragging:
                    piece_rects[selected_piece].x = event.pos[0] + offset_x
                    piece_rects[selected_piece].y = event.pos[1] + offset_y

        # Colorful background
        screen.fill((255, 200, 100))  # Adjust the RGB values for your preferred background color

        # Draw puzzle pieces on the screen
        for piece, rect in zip(pieces, piece_rects):
            screen.blit(piece, rect)

        # Display scoring information
        font = pygame.font.Font(None, 36)
        moves_text = font.render(f"Moves: {moves}", True, (0, 0, 0))
        screen.blit(moves_text, (10, 10))

        # Check if congrats message should be displayed
        if congrats_displayed:
            congrats_text = font.render("Well Done! Puzzle Completed!", True, (0, 255, 0))
            screen.blit(congrats_text, (width // 2 - 200, height // 2 - 50))

        pygame.display.flip()

        # Increment moves count when a piece is moved
        if dragging:
            moves += 1

    pygame.quit()

if __name__ == "__main__":
    main()
