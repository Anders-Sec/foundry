module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',
        'fix',
        'chore',
        'docs',
        'refactor',
        'test',
        'build',
        'ci',
        'perf',
        'style',
        'revert',
      ],
    ],
    'scope-empty': [0],
    'subject-case': [2, 'always', 'lower-case'],
  },
};
