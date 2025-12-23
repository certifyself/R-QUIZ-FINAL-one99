"""
AI Image Generation Service for SocraQuest Image Quiz
Generates images based on question text using OpenAI's image generation
"""
import os
import base64
import uuid
import asyncio
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Directory to store generated images
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def generate_quiz_image(question_text: str, topic_name: str = "") -> Optional[str]:
    """
    Generate an image for a quiz question using AI.
    
    Args:
        question_text: The question text to generate an image for
        topic_name: Optional topic name for context
    
    Returns:
        The URL path to the generated image, or None if generation fails
    """
    try:
        from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration
        
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            print("❌ EMERGENT_LLM_KEY not found in environment")
            return None
        
        # Create a prompt for image generation based on the question
        # We want an educational, clear image that represents the answer
        prompt = create_image_prompt(question_text, topic_name)
        print(f"🎨 Generating image with prompt: {prompt[:100]}...")
        
        # Initialize the image generator
        image_gen = OpenAIImageGeneration(api_key=api_key)
        
        # Generate the image
        images = await image_gen.generate_images(
            prompt=prompt,
            model="gpt-image-1",  # Using gpt-image-1 for quiz images
            number_of_images=1
        )
        
        if images and len(images) > 0:
            # Save the image to disk
            filename = f"quiz_img_{uuid.uuid4().hex[:12]}.png"
            filepath = os.path.join(UPLOAD_DIR, filename)
            
            with open(filepath, "wb") as f:
                f.write(images[0])
            
            # Return absolute URL for the image
            # Get the base URL from environment or use default
            base_url = os.environ.get('BASE_URL', 'https://mindgames-19.preview.emergentagent.com')
            image_url = f"{base_url}/uploads/{filename}"
            print(f"✅ Image generated and saved: {image_url}")
            return image_url
        else:
            print("❌ No image was generated")
            return None
            
    except Exception as e:
        print(f"❌ Error generating image: {str(e)}")
        return None


def create_image_prompt(question_text: str, topic_name: str = "") -> str:
    """
    Create an effective prompt for generating a quiz image.
    The prompt should result in a clear, educational image.
    """
    # Clean up the question text
    question = question_text.strip()
    
    # Remove common question prefixes
    prefixes_to_remove = [
        "Which famous landmark is shown in this image?",
        "What is shown in this image?",
        "What is pictured here?",
        "Identify the",
        "What is this?",
        "Which",
        "What",
    ]
    
    # Try to extract the subject from the question
    subject = question
    for prefix in prefixes_to_remove:
        if subject.lower().startswith(prefix.lower()):
            subject = subject[len(prefix):].strip()
            break
    
    # Build the prompt
    if topic_name:
        prompt = f"A clear, high-quality photograph of {subject}. Topic: {topic_name}. "
    else:
        prompt = f"A clear, high-quality photograph or illustration of {subject}. "
    
    prompt += "Educational style, well-lit, centered composition, suitable for a trivia quiz. "
    prompt += "No text or labels in the image."
    
    return prompt


def generate_quiz_image_sync(question_text: str, topic_name: str = "") -> Optional[str]:
    """
    Synchronous wrapper for generate_quiz_image.
    Use this in non-async contexts.
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate_quiz_image(question_text, topic_name))
        loop.close()
        return result
    except Exception as e:
        print(f"❌ Error in sync wrapper: {str(e)}")
        return None
