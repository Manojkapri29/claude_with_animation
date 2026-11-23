  const T = TIMELINE, cu = T.cues;
  to = 'm';
  pad(0.0, T.duration, ['D3', 'A3'], 0.02, { cut: 900, att: 0.4, rel: 0.4 });
  to = 's';
  sweep(5.2, 5.55, 0.01, 500, 2600, 0); sweep(7.45, 7.8, 0.01, 500, 2600, 0);
