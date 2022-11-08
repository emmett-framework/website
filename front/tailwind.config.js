module.exports = {
  darkMode: 'class',
  variants: {
    borderWidth: ['responsive', 'hover', 'focus'],
    visibility: ['responsive', 'group-hover']
  },
  theme: {
    screens: {
      port: [
        {max: '779px'},
        {min: '780px', max: '919px'}
      ],
      land: [
        {min: '920px'},
        {min: '1080px'},
        {min: '1280px'},
        {min: '1440px'}
      ]
    },
    extend: {
      borderWidth: {
        '1r': '0.25rem',
        '2r': '0.5rem'
      }
    }
  },
  purge: {
    enabled: process.env.NODE_ENV == "production",
    content: ['../app/templates/**/*.haml'],
  }
}
