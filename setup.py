from setuptools import setup, find_packages

setup(
        name='python-azlyrics-artist-scraper',
        packages=find_packages(),
        version='0.1',
        description='Python script to scrape artist text from azlyrics.com.',
        author='Justin Beall',
        author_email='jus.beall@gmail.com',
        url='https://github.com/DEV3L/python-azlyrics-artist-scraper',
        download_url='https://github.com/DEV3L/python-azlyrics-artist-scraper/tarball/0.1',
        keywords=['dev3l', 'azlyrics', 'beautifulsoup', 'python'],
        install_requires=[
            'beautifulsoup4==4.5.1',
            'requests==2.11.1'
        ],
        classifiers=[
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules'],
)
