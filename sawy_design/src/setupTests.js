```javascript
import { render } from '@testing-library/react';
import TailwindCSS from 'tailwindcss';

function SetupTests() {
  return (
    <div className="container flex justify-center items-center bg-blue-500">
      <h1>Welcome to the React Testing Library Tutorial</h1>
      <p>This is a simple app that demonstrates how to use the React Testing Library.</p>
    </div>
  );
}

test('renders correctly', () => {
  const { container } = render(<SetupTests />);

  expect(container).toMatchSnapshot();
});

describe('setup tests', () => {
  it('renders correctly with default settings', async () => {
    const { container } = render(<SetupTests />);

    expect(container).toHaveTextContent(/react/i);
  });

  it('renders correctly with custom settings', async () => {
    const { container } = render(<SetupTests settings={{ backgroundColor: 'red' }} />);

    expect(container).toHaveTextContent(/react/i);
  });
});
```