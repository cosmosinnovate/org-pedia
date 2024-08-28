/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  screens: {
    sm: '480px',
    md: '768px',
    lg: '976px',
    xl: '1440px',
  },
  theme: {
    extend: {
      borderRadius: {
        '1': '1px', 
      },
      fontSize: {
        '14': '14px',
        '18': '18px',
        '24': '24px',
      },
      fontWeight: {
        '700': '700',
      },
      textColor: {
        'bsk-gray-text': `#696969`,
        'bsk-label':'#344054'
      },
      borderColor: {
        'bsk-gray-input': `#D0D5DD`,
      }
    },
  },
  plugins: [],
}