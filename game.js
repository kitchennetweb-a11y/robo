// Robo game rules: what each event does. Pure (no DOM/three), so test.html can drive it.
// step(state, event, now) mutates state and returns an act {clip, loop, face, sfx, say, fx, delay} or null.
export const pick = a => a[Math.floor(Math.random() * a.length)];

// face name -> [eye texture, mouth texture] in face/
export const FACES = {
  normal: ['eye_normal_bot_1', 'mouth_normal'], happy: ['eye_happy', 'mouth_happy'], joy: ['eye_joy', 'mouth_smile'],
  sad: ['eye_sad', 'mouth_sad'], x: ['eye_x', 'mouth_O'], surprised: ['eye_normal_bot_1', 'mouth_O'],
  star: ['eye_star', 'mouth_happy'], heart: ['eye_heart', 'mouth_smile'], sleep: ['eye_blink', 'mouth_flat'],
  woozy: ['eye_x', 'mouth_flat'],
};
// sfx are the parent's own ElevenLabs voice lines: when one plays, Robo doesn't also say a phrase.

export const SAYS = {
  fall: ['oftadam', 'akh', 'vay', 'oh'], full: ['ser_shodam', 'boo_mide'],
};

export const REACT = {  // touch zone -> reaction
  head: { clip: 'HeadPoke', face: 'surprised', say: ['akh_saram', 'sar', 'in_sarame', 'yavash'] },
  face: { clip: 'Sneeze', face: 'surprised', sfx: 'face' },
  belly: { clip: 'BellyPoke', face: 'joy', sfx: 'belly' },
  foot: { clip: 'FootPoke', face: 'happy', sfx: 'feet' },
  hand: { clip: 'Wave', face: 'happy', sfx: 'hi' },
  arm: { clip: 'ThumbsUp', face: 'happy', sfx: 'arm' },
  antenna: { clip: 'Dizzy', face: 'x', sfx: 'antenna' },
};
const HEAD_SWIPE = { clip: 'HeadWobble', face: 'woozy', sfx: 'head' };
const LONELY = { clip: 'Wave', face: 'sad', sfx: 'bored' };  // nobody played for 2 minutes

export const FOOD = {
  apple: { emoji: '🍎', say: ['sib', 'sib_mikham', 'sib_khoshmaze', 'khoshmaze'] },
  banana: { emoji: '🍌', say: ['moz', 'moz_mikham', 'moz_dooset_daram', 'khoshmaze'] },
  milk: { emoji: '🥛', say: ['shir', 'shir_mikham', 'shir_khordam'] },
  water: { emoji: '💧', say: ['ab', 'ab_mikham', 'ab_khonak'] },
  bread: { emoji: '🍞', say: ['nan', 'nan_mikham', 'khoshmaze', 'nosh_jan'] },
};

// what Robo asks for (learning: the child hears the word and brings the thing) -> phrases, said in order
export const ASK = {
  apple: ['sib_mikham'], banana: ['moz_mikham'], bread: ['nan_mikham'], milk: ['shir_mikham'], water: ['ab_mikham'],
  ball: ['toop', 'bede_be_man'], car: ['mashin', 'bede_be_man'], teddy: ['khers', 'bede_be_man'], book: ['ketab', 'bede_be_man'],
};
// toys for the toy words: tap -> the toy comes to Robo (index.html moves it during the clip), then goes home
const TOYS = {
  car: { clip: 'Idle', loop: true, face: 'joy', say: 'mashin', fx: 'drive' },  // drive fx sends clipDone when parked again
  teddy: { clip: 'Hug', face: 'heart', say: ['khers', 'dooset_daram'] },
  book: { clip: 'Read', face: 'happy', say: 'ketab' },
};
const PRAISE = ['afarin', 'afarin_kheili_khoob', 'mamnoon'];
const got = (s, item) => {  // the child brought what Robo asked for: celebrate after the eat/kick
  s.want = null; return { clip: 'DanceJump', face: 'star', say: pick(PRAISE), fx: 'correct', item };
};
export const FALLS = [['Fall', 'GetUp'], ['FallBack', 'GetUpBack'], ['FallFront', 'GetUpFront'], ['FallApart', 'Reassemble']];
export const DANCES = [  // [clip, phrase, voice line]
  ['DanceWiggle', 'beraghs'], ['DanceSpin', 'becharkh'], ['DanceJump', null, 'jump'], ['DanceJump', 'dast_bezan']];
export const SILLY = [  // random thing to do when nobody has touched Robo for a while
  { clip: 'Fart', face: 'joy', fx: 'fart', say: ['oops', 'boo_mide', 'in_chi_bood'] },
  { clip: 'Sneeze', face: 'surprised', say: ['hapche', 'bebakhshid'] },
  { clip: 'Wave', face: 'happy', say: ['gorosnam', 'bia_bazi', 'biya_inja', 'ghaza_mikham'] },
  { clip: 'FootPoke', face: 'joy', say: ['bepar', 'dobare'] },
];

const IDLE = { clip: 'Idle', loop: true, face: 'normal' };
const once = r => ({ ...r, say: r.say && pick(r.say) });
export const S0 = () => ({ mode: 'idle', next: [], taps: [], fed: [], want: null });

export function step(s, ev, now = Date.now()) {
  const free = s.mode === 'idle' || s.mode === 'react';
  switch (ev.type) {
    case 'greet':
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; return { clip: 'Wave', face: 'happy', sfx: 'hi' };
    case 'tap':
      if (s.mode === 'sleep') return wake(s);
      if (s.mode === 'hide') return step(s, { type: 'peek' }, now);  // tapping the hidden Robo = peekaboo!
      if (!free || !REACT[ev.zone]) return null;  // unknown zone: ignore rather than get stuck in 'react'
      s.taps = s.taps.filter(t => now - t < 2000).concat(now);
      if (s.taps.length >= 4) {  // too many pokes: fall over, wait, get up
        const [fall, up] = pick(FALLS); s.taps = []; s.mode = 'react';
        s.next = [{ clip: up, face: 'happy', sfx: 'yay', delay: 900 }];
        return { clip: fall, face: 'x', say: pick(SAYS.fall) };
      }
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; return once(REACT[ev.zone]);
    case 'feed': {
      if (!free) return null;
      s.fed = s.fed.filter(t => now - t < 60000).concat(now); s.mode = 'react'; s.next = [];
      if (s.want === ev.food) s.next.push(got(s, ev.food));
      else if (s.want) s.next.push({ clip: 'Wave', face: 'happy', say: ASK[s.want] });  // not what he asked for: eat it anyway, ask again
      if (s.fed.length >= 3) { s.fed = []; s.next.push({ clip: 'Fart', face: 'joy', fx: 'fart', say: pick(SAYS.full) }); }
      const drink = ev.food === 'milk' || ev.food === 'water';  // drinks: cup to the mouth; fx picks the cup
      return { clip: drink ? 'Drink' : 'Eat', face: 'heart', sfx: 'feed', fx: drink ? ev.food : undefined };  // FOOD[].say: tray tap
    }
    case 'headSwipe':
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; return HEAD_SWIPE;
    case 'bored':
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; return once(pick(SILLY));
    case 'lonely':
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; return LONELY;
    case 'bed':
      if (s.mode === 'sleep') return wake(s);
      if (!free) return null;
      s.mode = 'sleep'; s.next = []; return { clip: 'Sleep', loop: true, face: 'sleep', fx: 'night', sfx: 'sleep' };
    case 'speaker':
      if (s.mode === 'dance') { s.mode = 'idle'; return { ...IDLE, face: 'happy', fx: 'musicOff', sfx: 'yay' }; }
      if (!free) return null;
      s.mode = 'dance'; s.next = []; return { clip: 'DanceWiggle', loop: true, face: 'star', fx: 'music', sfx: 'dance' };
    case 'danceStep': {
      if (s.mode !== 'dance') return null;
      const [clip, say, sfx] = pick(DANCES); return { clip, loop: true, say: say || undefined, sfx };
    }
    case 'ball':  // the ball rolled into Robo: hop and kick it back
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; s.next = s.want === 'ball' ? [got(s, 'ball')] : [];
      return { clip: 'FootPoke', face: 'joy', sfx: 'ball', fx: 'kickBall' };
    case 'car': case 'teddy': case 'book':
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; s.next = s.want === ev.type ? [got(s, ev.type)] : [];
      return TOYS[ev.type];
    case 'ask':  // Robo asks for something (voice only first: listening practice)
      if (s.mode !== 'idle' || s.want) return null;
      s.want = pick(Object.keys(ASK)); s.mode = 'react';
      return { clip: 'Wave', face: 'happy', say: ASK[s.want], fx: 'asked', item: s.want };
    case 'askHint':  // no answer yet: ask again (the app also highlights the thing)
      if (s.mode !== 'idle' || !s.want) return null;
      return { face: 'happy', say: ASK[s.want] };
    case 'askEnd':  // nobody answered: drop it quietly
      if (!s.want) return null;
      s.want = null; return { fx: 'askDone' };
    case 'bubbles':  // tap the bubble bottle: excited hop while bubbles float up (the child pops them)
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; return { clip: 'FootPoke', face: 'star', sfx: 'bubbles', fx: 'bubbles' };
    case 'peek':  // blanket: 1st tap hides Robo under it, 2nd tap (or a timer) whisks it off and he pops out
      if (s.mode === 'hide') { s.mode = 'react'; return { clip: 'DanceJump', face: 'joy', sfx: 'peek', fx: 'blanketOff' }; }
      if (s.mode !== 'idle') return null;
      s.mode = 'hide'; return { clip: 'Idle', loop: true, face: 'normal', fx: 'blanketOn' };
    case 'rocket':  // tap the toy rocket: rise half way, loop around the room (fx 'orbit' sends clipDone when back), land
      if (s.mode !== 'idle') return null;
      s.mode = 'react'; s.next = [{ clip: 'RocketFly', loop: true, fx: 'orbit' }, { clip: 'RocketLand', face: 'happy' }];
      return { clip: 'RocketLaunch', face: 'star', sfx: 'rocket' };
    case 'swipeUp':
      if (!free) return null;
      s.mode = 'fly'; s.next = []; return { clip: 'Fly', loop: true, face: 'joy', sfx: 'fly', fx: 'flyTimer' };
    case 'flyEnd':
      if (s.mode !== 'fly') return null;
      s.mode = 'idle'; return IDLE;
    case 'clipDone':
      if (s.mode !== 'react') return null;
      if (s.next.length) return s.next.shift();
      s.mode = 'idle'; return IDLE;
  }
  return null;
}
function wake(s) { s.mode = 'react'; s.next = []; return { clip: 'Wave', face: 'happy', sfx: 'wake', fx: 'day' }; }
