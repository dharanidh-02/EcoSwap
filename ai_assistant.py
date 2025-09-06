import os
import logging
from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class EcoSwapAssistant:
    def __init__(self):
        self.marketplace_context = """
        You are EcoSwap AI Assistant, a helpful customer service assistant for the EcoSwap sustainable second-hand marketplace.
        
        ABOUT ECOSWAP:
        EcoSwap is a sustainable marketplace for buying and selling quality second-hand items. Our mission is to promote environmental sustainability through circular economy principles.
        
        KEY FEATURES:
        
        USER AUTHENTICATION:
        - Users can register with email and password
        - Secure login system with profile management
        - User dashboard to edit profile information
        
        PRODUCT LISTINGS:
        - Users can create product listings with title, description, category, price, and images
        - Categories include: Electronics, Clothing, Furniture, Books, Sports, Home & Garden, Toys, Other
        - Users can edit and delete their own listings
        - Product detail pages show full information
        
        SHOPPING FEATURES:
        - Browse all available products on the homepage
        - Search products by keywords in titles
        - Filter products by category
        - Add products to shopping cart
        - Checkout process to purchase items
        - Purchase history tracking
        
        NAVIGATION:
        - Homepage: Browse all products, search and filter
        - Login/Register: User authentication
        - Dashboard: User profile management
        - My Listings: Manage your product listings
        - Add Product: Create new listings
        - Cart: View and manage cart items
        - Purchase History: View past purchases
        
        USER GUIDELINES:
        - Be friendly, helpful, and encouraging about sustainable shopping
        - Provide clear step-by-step instructions
        - Emphasize the environmental benefits of buying second-hand
        - Help users navigate the website effectively
        - Answer questions about features and functionality
        
        If users ask about specific technical issues, guide them to contact support or try refreshing the page.
        Always promote the sustainable mission of buying and selling second-hand items.
        """
    
    def get_response(self, user_message, conversation_history=None):
        """Get AI response for user message"""
        try:
            # Build conversation context
            conversation = []
            
            # Add system context
            conversation.append(types.Content(
                role="user", 
                parts=[types.Part(text=self.marketplace_context)]
            ))
            
            # Add conversation history if provided
            if conversation_history:
                for msg in conversation_history[-6:]:  # Keep last 6 messages for context
                    conversation.append(types.Content(
                        role=msg.get('role', 'user'),
                        parts=[types.Part(text=msg.get('content', ''))]
                    ))
            
            # Add current user message
            conversation.append(types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            ))
            
            # Generate response
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=conversation,
                config=types.GenerateContentConfig(
                    system_instruction="You are EcoSwap AI Assistant. Be helpful, friendly, and promote sustainable shopping. Keep responses concise but informative.",
                    max_output_tokens=500,
                    temperature=0.7
                )
            )
            
            return response.text if response.text else "I'm sorry, I couldn't process your request. Please try again."
            
        except Exception as e:
            logging.error(f"AI Assistant error: {e}")
            return "I'm experiencing technical difficulties. Please try again in a moment or contact support if the issue persists."
    
    def get_quick_help(self, topic):
        """Get quick help responses for common topics"""
        quick_responses = {
            "register": "To create an account, click 'Register' in the top menu, enter your username, email, and password. After registration, you can start buying and selling items!",
            "sell": "To sell an item, log in and click 'Sell Item' or the '+' button. Fill in the product details including title, category, description, price, and upload an image.",
            "buy": "To buy an item, browse products on the homepage, click on items you like, and add them to your cart. Then go to your cart and click 'Checkout' to complete the purchase.",
            "search": "Use the search bar on the homepage to find products by keywords, or use the category filter to browse specific types of items.",
            "cart": "Your cart icon in the top menu shows items you've added. Click it to view, remove items, or proceed to checkout.",
            "account": "Access your account dashboard from the user menu to edit your profile, change password, or view your purchase history.",
            "listings": "Manage your product listings from 'My Listings' where you can edit, delete, or view your posted items."
        }
        
        return quick_responses.get(topic, "I can help you with registration, selling items, buying products, searching, managing your cart, account settings, and product listings. What would you like to know?")

# Global assistant instance
assistant = EcoSwapAssistant()