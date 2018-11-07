from graphqlclient import GraphQLClient

client = GraphQLClient('http://localhost:4466')


def update_image_status(status, id):

    result = client.execute('''
    mutation {{
      updateImage(data: {{status: "{}"}}, where: {{id: "{}"}}) {{
        status
      }}
    }}
    '''.format(status, id))

    print(result)


def update_image_size(width, height, id):

    result = client.execute('''
    mutation {{
      updateImage(data: {{width: {}, height: {}}}, where: {{id: "{}"}}) {{
        status
      }}
    }}
    '''.format(width, height, id))

    print(result)


def create_postits(postits, image_id):
    for postit in postits:
        result = client.execute('''
        mutation {{
          createPostit(data: {{image: {{connect: {{id: "{}"}}}}, url: "{}", detectedText: "{}", x: {}, y: {}, width: {}, height: {}}}) {{
            id
            url
          }}
        }}
        '''.format(image_id, postit['url'], postit['text'], postit['x'], postit['y'], postit['width'],
                   postit['height']))

        print(result)
