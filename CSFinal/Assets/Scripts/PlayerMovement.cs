using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;

public class PlayerMovement : MonoBehaviour
{
    public bool grounded = false;
    Vector3 speed = new Vector3(0, 0, 0);
    public float xDir = 0;
    float moveSpeedRatio = 0.02f;
    float moveSpeedCap = 0.16f;
    float baseJumpSpeed = 0.25f;
    float footPos = 0;
    float gravity = 0.02f;
    bool jumped = false;
    int jumpTimer = 0;
    float terminalVelocity = -0.30f;
    public BoxCollider2D boxCollider2d;
    public Rigidbody2D rigidbody2D;
    public SpriteRenderer sprRend;
    void Start()
    {
        Rigidbody2D rigidbody2D = GetComponent<Rigidbody2D>();
        BoxCollider2D boxCollider2d = GetComponent<BoxCollider2D>();
        SpriteRenderer sprRend = GetComponent<SpriteRenderer>();
    }
    
    // Update is called once per frame
    void Update()
    {
        xDir = 0;
        //Input
        if (Input.GetKey(KeyCode.LeftArrow))
        {
            xDir -= 1;
            sprRend.flipX = true;
        }
        if (Input.GetKey(KeyCode.RightArrow))
        {
            xDir += 1;
            sprRend.flipX = false;
        }
        if (Input.GetKeyDown(KeyCode.UpArrow) && grounded)
        {
            Debug.Log("jump");
            jumped = true;
            speed.y = baseJumpSpeed;
            jumpTimer = 8;
        }
        if (Input.GetKeyUp(KeyCode.W))
        {
            jumpTimer = 0;
            jumped = false;
        }
    }

    void FixedUpdate()
    {
        grounded = IsGrounded();
        if (jumped == true && jumpTimer > 0)
        {
            speed.y += 0.022f;
            jumpTimer--;
        }

        if (xDir == 0)
        {
            if (grounded)
            {
                if (Math.Abs(speed.x) < 0.02)
                {
                    speed.x = 0;
                }
                else
                {
                    speed.x -= Math.Sign(speed.x) * 0.02f;
                }
            }
            else
            {
                if (Math.Abs(speed.x) < 0.005)
                {
                    speed.x = 0;
                }
                else
                {
                    speed.x -= Math.Sign(speed.x) * 0.005f;
                }
            }
        }
        if (Math.Abs(speed.x) < moveSpeedCap || Math.Sign(speed.x) != Math.Sign(xDir))
        {
            if (grounded)
            {
                speed.x += moveSpeedRatio * xDir;
            }
            else
            {
                speed.x += moveSpeedRatio /2 * xDir;
            }
        }
        Vector3 tmp = rigidbody2D.gameObject.transform.position; 
        if (!grounded)
        {

            if (speed.y < 0)
            {
                speed.y -= gravity * 1.5f;
            }
            else
            {
                speed.y -= gravity;
            }
            
        }
        if (grounded && speed.y < 0)
        {
            Debug.Log("hit ground");
            speed.y = 0;
        }
        if (IsHittingCeiling())
        {
            speed.y = -0.05f;
        }

        if ((IsHittingLeftWall() && speed.x < 0) || (IsHittingRightWall() && speed.x > 0))
        {
            speed.x = 0;
        }
        footPos = tmp.y - .5f;
        rigidbody2D.MovePosition(tmp + speed);
    }

    public bool IsGrounded()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.down, 0.1f);
        return hit.collider != null;
    }
    public bool IsHittingCeiling()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.up, 0.01f);
        return hit.collider != null;
    }

    public bool IsHittingRightWall()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.right, 0.01f);
        return hit.collider != null;
    }

    public bool IsHittingLeftWall()
    {
        RaycastHit2D hit = Physics2D.BoxCast(boxCollider2d.bounds.center, boxCollider2d.bounds.size, 0, Vector2.left, 0.01f);
        return hit.collider != null;
    }
}
