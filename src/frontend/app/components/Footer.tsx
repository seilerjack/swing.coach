
export default function Footer() {
  return (
    <footer className="bg-gray-900 px-6 py-16 text-gray-300">
        <div className="mx-auto max-w-7xl grid gap-12 md:grid-cols-3">
          <div>
            <h3 className="font-semibold text-white">SwingCoach.io</h3>
            <p className="mt-4 text-sm">
              AI-powered golf swing analysis that helps you improve your game
              with professional-grade insights and personalized coaching.
            </p>
          </div>

          <div>
            <h4 className="font-semibold text-white">Product</h4>
            <ul className="mt-4 space-y-2 text-sm">
              <li><a href="#features">Features</a></li>
              <li><a href="/analyze">Analyze</a></li>
              <li><a href="#how-it-works">How to Use</a></li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-white">Company</h4>
            <ul className="mt-4 space-y-2 text-sm">
              <li>About</li>
              <li>Blog</li>
              <li>Contact</li>
              <li>Support</li>
            </ul>
          </div>
        </div>

        <div className="mx-auto mt-12 max-w-7xl border-t border-gray-700 pt-6 text-sm flex justify-between">
          <span>© 2026 SwingCoach.io. All rights reserved.</span>
          <div className="flex gap-6">
            <span>Privacy Policy</span>
            <span>Terms of Service</span>
          </div>
        </div>
    </footer>
  );
}
