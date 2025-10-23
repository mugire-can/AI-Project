"""
Script to generate audio jingle using TTS (Text-to-Speech)
Requires: pip install gTTS pydub
Note: gTTS uses Google's TTS API and requires internet connection
"""

from gtts import gTTS
import os

def create_jingle_audio():
    """Create audio file for PACA jingle with female voice"""
    
    # Jingle text (spoken parts only)
    jingle_text = """
    Du soleil de Provence à ta table,
    Des fruits et légumes incomparables!
    Directement du producteur,
    Pour toi, que du bonheur!
    
    Frais, local, et c'est royal!
    De la mer aux montagnes, quelle merveille!
    Tomates, melons, fruits du soleil,
    PACA dans ton panier, c'est ça la vie!
    
    Le goût du Sud chez toi!
    Télécharge maintenant!
    """
    
    print("Génération de l'audio du jingle...")
    
    try:
        # Create TTS object with French language
        # gTTS uses female voice by default for French
        tts = gTTS(text=jingle_text, lang='fr', slow=False)
        
        # Save the audio file
        output_file = "jingle_paca.mp3"
        tts.save(output_file)
        
        print(f"✓ Audio généré avec succès: {output_file}")
        print(f"✓ Emplacement: {os.path.abspath(output_file)}")
        print("\nNOTE: Ce fichier contient uniquement les paroles parlées.")
        print("Pour un vrai jingle, il faudrait:")
        print("  1. Ajouter la musique de fond (guitare, mandoline)")
        print("  2. Enregistrer avec un(e) chanteur(se) professionnel(le)")
        print("  3. Mixer avec des effets sonores de marché provençal")
        
        return output_file
        
    except Exception as e:
        print(f"✗ Erreur lors de la génération: {e}")
        print("\nAssurez-vous d'avoir installé les dépendances:")
        print("  pip install gTTS")
        return None

if __name__ == "__main__":
    create_jingle_audio()
