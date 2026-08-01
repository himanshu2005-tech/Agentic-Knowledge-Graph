// Auto-generated Code Vault for 'AmbientDroneSoundscape' [Supercollider]

(
SynthDef(\bass, { arg out = 0, freq = 20, amp = 0.5, cutoff = 100;
    var sig, env;
    env = EnvGen.ar(Env.perc(0.1, 2, amp, -2), doneAction: Done.freeSelf);
    sig = SinOsc.ar(freq) * env;
    sig = LPF.ar(sig, cutoff);
    Out.ar(out, sig ! 2);
}).add;

SynthDef(\chime, { arg out = 0, freq = 2000, amp = 0.1, decay = 2;
    var sig, env, trig;
    trig = Dust.ar(2);
    env = EnvGen.ar(Env.perc(0.01, decay, amp, -4), gate: trig, doneAction: Done.freeSelf);
    sig = Resonz.ar(WhiteNoise.ar(0.01), freq, 0.1) * env;
    sig = sig * 2;
    Out.ar(out, sig ! 2);
}).add;

SynthDef(\reverb, { arg out = 0, in = 0;
    var sig;
    sig = In.ar(in, 2);
    sig = FreeVerb2.ar(sig[0], sig[1], 0.5, 0.7, 0.2);
    Out.ar(out, sig);
}).add;

s.boot;

~bass = Synth(\bass, [\freq, 30, \cutoff, 50, \amp, 0.4]);
~chime = Synth(\chime, [\freq, 2500, \amp, 0.2, \decay, 1.5]);
~reverb = Synth(\reverb, [\in, 0]);

~bass2 = Synth(\bass, [\freq, 40, \cutoff, 70, \amp, 0.3]);
~chime2 = Synth(\chime, [\freq, 2000, \amp, 0.1, \decay, 2]);

~bass3 = Synth(\bass, [\freq, 50, \cutoff, 90, \amp, 0.2]);
~chime3 = Synth(\chime, [\freq, 2200, \amp, 0.15, \decay, 1.8]);

s.plotTree;
)

(
Task({
    var now = Date.date;
    var duration = 600; // 10 minutes
    var endTime = now + duration;
    while ({ now < endTime }, {
        ~bass.set(\freq, rrand(20, 60));
        ~bass.set(\cutoff, rrand(50, 150));
        ~bass.set(\amp, rrand(0.2, 0.5));
        ~bass2.set(\freq, rrand(30, 70));
        ~bass2.set(\cutoff, rrand(70, 170));
        ~bass2.set(\amp, rrand(0.1, 0.4));
        ~bass3.set(\freq, rrand(40, 80));
        ~bass3.set(\cutoff, rrand(90, 190));
        ~bass3.set(\amp, rrand(0.1, 0.3));
        ~chime.set(\freq, rrand(2000, 3000));
        ~chime.set(\amp, rrand(0.1, 0.3));
        ~chime.set(\decay, rrand(1, 3));
        ~chime2.set(\freq, rrand(1800, 2800));
        ~chime2.set(\amp, rrand(0.05, 0.2));
        ~chime2.set(\decay, rrand(1.5, 3.5));
        ~chime3.set(\freq, rrand(1500, 2500));
        ~chime3.set(\amp, rrand(0.05, 0.2));
        ~chime3.set(\decay, rrand(1.5, 3.5));
        now = Date.date;
        10.wait;
    });
}).start;
)
