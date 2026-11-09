from __future__ import annotations

import re
from urllib.parse import urlparse


COMPANIES = (
    "Williams Companies",
    "Southern Company",
    "Lockheed Martin",
    "Fiserv",
    "Royal Caribbean Ltd.",
    "Canfield Scientific",
    "Zodiac Interactive",
)

PROJECTS = (
    ("portfolio-github", "JavaScript + React + Vite", "GitHub Portfolio Website"),
    (
        "java-playwright",
        "Java + Playwright + OpenCV + JUnit",
        "Java + Playwright Automation Project",
    ),
    (
        "csharp-mobile",
        "C# + Selenium + Appium + NUnit",
        "C# + Selenium + Appium + NUnit Automation Project",
    ),
    (
        "java-mobile",
        "Java + Selenium + Appium + Charles Proxy + TestNG",
        "Java + Selenium + Appium + Charles Proxy + TestNG Automation Project",
    ),
    (
        "jmeter-jenkins",
        "JMeter + Jenkins CI/CD",
        "JMeter + Jenkins API Automation Project",
    ),
    (
        "cypress-typescript-cicd",
        "Cypress + TypeScript + Allure + GitHub Actions",
        "Cypress + TypeScript + Allure + GitHub Actions CI/CD Project",
    ),
)

DEMO_LINKS = (
    (
        "portfolio-github",
        "GitHub repository",
        "https://github.com/alexbashchuk/alexbashchuk.github.io",
    ),
    ("portfolio-github", "GitHub Pages site", "https://alexbashchuk.github.io"),
    (
        "java-playwright",
        "GitHub repository",
        "https://github.com/alexbashchuk/playwright-java-demo",
    ),
    (
        "csharp-mobile",
        "GitHub repository",
        "https://github.com/alexbashchuk/CSharp_Selenium_Appium_NUnit",
    ),
    (
        "java-mobile",
        "RCCL-Mobile-Test.pptx",
        "https://alexbashchuk.github.io/assets/RCCL-Mobile-Test-CY1r6d87.pptx",
    ),
    (
        "java-mobile",
        "GitHub repository",
        "https://github.com/alexbashchuk/Java-TestNG-Selenium-Appium-ProxyServer",
    ),
    (
        "jmeter-jenkins",
        "GitHub repository",
        "https://github.com/alexbashchuk/JMeter-Test",
    ),
    (
        "jmeter-jenkins",
        "GitHub repository",
        "https://github.com/alexbashchuk/alexbashchuk.github.io",
    ),
    (
        "cypress-typescript-cicd",
        "TypeScript-Cypress-CICD repository",
        "https://github.com/alexbashchuk/TypeScript-Cypress-CICD",
    ),
    (
        "cypress-typescript-cicd",
        "alexbashchuk.github.io",
        "https://github.com/alexbashchuk/alexbashchuk.github.io",
    ),
)

YOUTUBE_VIDEOS = (
    ("java-playwright", "7d74GlFB3Lg", "Java Playwright Test"),
    ("csharp-mobile", "WYbm4WLOnes", "C Sharp Selenium Appium NUnit"),
    ("java-mobile", "OImSZfvOeYk", "RCCL Java Selenuim Appium"),
    ("java-mobile", "-Y6T5DNOoWA", "HTML TestNG Report"),
    ("jmeter-jenkins", "VEgMSr7PkVs", "JMeter Jenkins"),
    ("cypress-typescript-cicd", "ePLVuEhLe9U", "Cypress TS Local"),
    ("cypress-typescript-cicd", "LgTh6r9JWVY", "Cypress TS GitActions"),
)

SECTION_HEADINGS = (
    "Professional Summary",
    "Technical Skills",
    "Professional Experience",
    "Education",
    "Certifications",
    "My QA Automation Demo Projects",
)


def heading_slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def destination_slug(destination: str) -> str:
    parsed = urlparse(destination)
    last_path_part = parsed.path.rstrip("/").split("/")[-1]
    return heading_slug(last_path_part or parsed.netloc)


def inventory_for_route(route: str) -> list[tuple[str, str]]:
    return [
        (label, href)
        for project_route, label, href in DEMO_LINKS
        if project_route == route
    ]


def project_heading_for_route(route: str) -> str:
    return next(heading for project_route, _, heading in PROJECTS if project_route == route)


def youtube_url(video_id: str) -> str:
    return f"https://youtu.be/{video_id}"
