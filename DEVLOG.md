# Plate Finder Devlog

## 2025-03-16 21:30

Docs link: <https://docs.google.com/document/d/1QooWeBN8u-bb2vmEzhXGpLazZrnmHgQoezg5DMJX2Hg/edit?tab=t.0>

I can use an existing model which helps things a lot. Google search gives me <https://github.com/ankandrew/open-image-models> and there's a bounding box class at <https://github.com/ankandrew/open-image-models/blob/26e18f4f6be3319cce49f1fb9af680ef4ca1fc3d/open_image_models/detection/core/base.py#L8>.

OpenCV or pillow can probably grab that for the larger view, will install both.

Using Python for speed of development. Don't like the language honestly, weak typing and awful package ecosystem, but it's the tool for the job.

Everything is in pypi, simple for uv to grab the deps. Will toss in ye olde Dockerfile and deploy at <railway.com> just like Spectacles-2-Unitree project (that I just spent all day containerizing; thankfully no need for C++ bindings here!).

Not going to do a fancy React frontend or set up TS transpilation tooling, just basic web template with a single vanilla JS file that Claude can probably oneshot.

Fake map data, probably OpenStreetMap provides a dropin `<script/>` that I can nav to.

Will use the same container for devcontainer and runtime for speed. Normally would optimize that via caching, `slim` variants and such.

Onwards!

## 22:00

Grabbing this dataset: <https://universe.roboflow.com/kanwal-masroor-gv4jr/yolov7-license-plate-detection/dataset/3#>

## 22:15

Grabbed $0.98 TLD <https://platefinder.space> from Namecheap.

LLMs can probably oneshot this given the scope, will see. Obviously, in a production system, I'd have to game out a ton of other concerns, wouldn't trust an LLM in that case because they don't have the context (ha ha) to build a production system -- details in my head, but hard to fit _all_ of that as prompting guidelines; might as well write it mostly wholesale. Know your tools...

## 22:30

Addresses dataset with geolocation: <https://www.kaggle.com/datasets/zubairatha/san-francisco-murals-geolocation-dataset>, that will come in handy for map later.

In a real use-case I'd use SmartyStreets to validate addresses and grab geolocation coords, they've been solid in my experience, and the minutia of address validation in the US alone is insane: worth paying for the API.

1.4G of plate images in that dataset, going to filter this down to 1024 images for the demo: `ls *.jpg | shuf | tail -n +$((1024 + 1)) | xargs -I{} rm "{}"`. Down to ~100M now.

## 23:45

Claude basically oneshot a MVP. (Minor prompting to clarify and fix bugs). Some considerations come to mind:

**Classification and bounding box regression side of things:**

1. In a real project, I'd spend a lot of time evaluating models on as big a dataset as I could muster before writing a single line of production code. That means a bunch of research to pull models, read papers, and evaluate a bunch of them on real-world datasets. It's one thing to see performance benchmarks on particular datasets, but in the real world you just have to see for yourself. That way I could also evaluate latency and false-positive rates.
2. The model I have currently is just _okay_, but I actually think I'll leave it that way: it demonstrates why this is important.
3. Multiple image processing pipelines and ensemble models (not architecturally, I mean just chaining API calls and/or running local models in concert or sequence) would be one approach. For example, if we have a low-confidence detection, it might be worthwhile to call a larger, slower, or more expensive model after running the first-line light and fast bounding box extraction.
4. Using secondary, slower models is also important because it lets you evaluate prod's performance on real-world data as it comes in. Use slow models (and humans) to review a portion of things after-the-fact and continually benchmark things.

**Software architecture:**

First pass is a single Python file, and a template that has all of the JS inlined, pulling from CDNs with `<link href...>`.

I strongly prefer keeping all source in-repo. `href`ing blindly from CDNs isn't great because:
- Magnet for supply chain attacks
- No guarantee of source stability (could have breaking changes introduced if improperly managed) or long-term availability

I'd also write things API-first, use an OpenAPI spec to get codegen for clients which could be bundled, minified, and packaged up appropriately into an SDK (npm for JS clients). Then keep an org-internal NPM repo.

**General thoughts:**

This takehome is too simple IMO, doesn't really distinguish deep SWE knowledge from what can be "vibe-coded" and slapped together in three hours. Hence why I'm spending time producing these organic, human-written tokens -- chains of thought -- uh, words. It's right on the pareto frontier of what LLMs can trivially churn out with some simple iteration, it doesn't extract the underlying experience a human can bring to bear.

Do I have recommendations for how to actually test for that? What would I do if I were hiring a SWE? Just talk to them, I guess, see what they bring up. Real knowledge and experience should bring *nuance* and consideration of long-term secondary and tertiary concerns; something LLM vibe-coding can't (yet) do.

Million times better than Leetcode though!

Time to refine.

## 00:15

Clicking through the site to check out performance on this model.

- A deskew pipeline would be nice in addition to bounding boxes.
- This model seems to struggle with images where the plate fills the entire frame, or images with heavy noise. Some mitigation strategies:
  - Try some denoising filters
  - Resize image smaller and add black padding to borders

Also some false-positives where tiny bounding boxes are returned. Going to add a quick filter to discard these.

## 01:00

Inline CSS needs work, needs to be moved to a separate file and hand-written. Will ditch Bootstrap.

Sometimes images fail to be base64 encoded: `Warning: Empty image received in encode_image_to_base64`. Need to validate that.

Deployed MVP to <https://platefinder.space> via Railway.