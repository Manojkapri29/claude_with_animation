"""Text for each 16:9 thumbnail. kind: t = big text, b = parchment banner, r = red strip. Art: out/thumbs/art{N}.png"""
Y, W_, R = '#ffd21f', '#ffffff', '#c8161d'
SPEC = {
 1: [('t', '12 साल का', 130, Y), ('t', 'बेघर राजकुमार', 130, Y), ('t', 'जिसने हिंदुस्तान जीत लिया!', 82, W_), ('b', 'बाबर, पानीपत और मुग़ल साम्राज्य का उदय-पतन', 52)],
 2: [('t', '12 साल का', 120, Y), ('t', 'बादशाह', 175, W_), ('t', 'जिसकी रगों में', 80, W_), ('t', 'तैमूर और चंगेज़ का', 90, Y), ('t', 'ख़ून था!', 90, W_)],
 3: [('t', '12,000 ने', 130, W_), ('t', '1,00,000 को', 145, Y), ('t', 'कैसे हराया?', 130, W_), ('b', 'बाबर की वो चाल', 80)],
 4: [('t', 'जब 1,000', 130, W_), ('t', 'जंगी हाथी', 155, Y), ('t', 'अपनी ही सेना पर', 88, W_), ('t', 'टूट पड़े!', 145, Y)],
 5: [('b', 'बाबर और पानीपत', 86), ('t', 'क्विज़', 165, Y), ('r', '5 सवाल, 5 सेकंड!', 78), ('t', 'कितने सही?', 110, W_)],
 6: [('b', 'मुग़ल साम्राज्य', 96), ('t', 'क्विज़', 165, Y), ('r', 'उदय से पतन तक • 5 सवाल', 66), ('t', 'कितने सही कर पाए?', 92, W_)],
}
NAMES = {1: 'thumb1-main-video-16x9', 2: 'thumb2-reel1-12-saal-ka-badshah-16x9', 3: 'thumb3-reel2-babur-ki-chaal-16x9',
         4: 'thumb4-reel3-haathi-16x9', 5: 'thumb5-quiz1-babur-panipat-16x9', 6: 'thumb6-quiz2-mughal-samrajya-16x9'}

# Prompts for tools/thumb_art.py (free FLUX art). English, describe people + scene, NO text.
ART = {
 1: 'young Timurid prince Babur, 12 years old, jeweled turban, looking at camera, burning Panipat battlefield and war elephants behind',
 2: '12-year-old Central Asian prince in 1490s Timurid royal attire, ornate jeweled turban, determined eyes looking at camera, ghostly figures of Timur and Genghis Khan in the smoky sky behind',
 3: 'Mughal emperor Babur in armour on horseback, raised sword, cannons firing behind a wall of wooden carts, huge Afghan army charging, dust and smoke, Panipat 1526',
 4: 'panicked armoured Indian war elephants stampeding through their own soldiers, cannon smoke and fire, 16th century battlefield, chaos',
 5: 'thoughtful Babur in Timurid armour holding an old map, Panipat battlefield at dusk behind, mysterious mood',
 6: 'three Mughal emperors standing together in royal robes in front of the Taj Mahal at sunset, regal, majestic',
}
