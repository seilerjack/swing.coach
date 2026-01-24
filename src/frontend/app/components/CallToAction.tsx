
export default function CallToAction() {
  return (
    <section className="px-6 py-24">
        <div className="mx-auto max-w-5xl rounded-3xl bg-gradient-to-br from-gray-900 to-gray-800 px-10 py-16 text-center text-white">
          <h2 className="text-3xl font-bold">
            Ready to Analyze Your Swing?
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-gray-300">
            Join thousands of golfers who have improved their game with
            SwingCoach.io. Start your journey to a better swing today.
          </p>

          <div className="mt-10 flex flex-col justify-center gap-4 sm:flex-row">
            <a
              href="/analyze"
              className="
                rounded-lg bg-white px-6 py-3 font-medium text-black
                transition-all duration-200
                hover:scale-105 active:scale-95
                "
            >
              Upload Swing Video →
            </a>
            {/* <button className="
              rounded-lg border border-white px-6 py-3
              transition-all duration-200
              hover:scale-105 active:scale-95
              ">
              Learn More
            </button> */}
          </div>

          {/* <p className="mt-6 text-sm text-gray-400">
            No credit card required · Free trial available
          </p> */}
        </div>
      </section>
  );
}
